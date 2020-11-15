#### BIT: Check for sign of bitwise operation

##### Regex

```regex
\(\s*((?:(?P<aux1>\((?:[^()]++|(?&aux1))*\))|[\w.])++)\s*&\s*((?:(?&aux1)|[\w.])+)\s*\)\s*>\s*0
```

##### Examples

```Java
CASE1 
if ((e.getChangeFlags() & e.PARENT_CHANGED) > 0)
CASE2    
if ((delta.getKind() & IResourceDelta.CHANGED) > 0 && (delta.getFlags() & IResourceDelta.MARKERS) > 0)
CASE3    
  int a = 1; int b = -1;
  Boolean test_var1 = (a&b)>0;
  int     test_var2 = -1;
  if(test_var1&& test_var2 >0){
            System.out.println("branch1");
  }
// (a&b)>0 will be matched, test_var1&& test_var2 >0 will not
```

##### 实现思路

由于无法得知变量内部的具体大小，只能匹配形如 （a & b) > 0的形式，提醒原来的代码可能会出现 取 & 小于 0的情况（最常见的错误来自于 -1由补码表示）用之前的正则表达式可以匹配。

#### BIT: Check to see if ((…) & 0) == 0 (BIT_AND_ZZ)

##### Regex

`\(\s*((?:(?P<aux1>\((?:[^()]++|(?&aux1))*\))|[\w.])++)\s*&\s*0\s*\)\s*==\s*0`

##### Examples

```Java
CASE 1
if ((e.getChangeFlags() & 0) == 0)
CASE 2
//由于我把两个pattern放在同一个类里，可以检测一行的两个信息
if ((e.getChangeFlags() & 0) == 0 &&(e.getChangeFlags() & e.PARENT_CHANGED > 0))
```

##### 实现思路

这个pattern 也在incompat_mask 类里，在原来的spotbugs代码中会获取具体变量的值。所以我们这里只能比较常量0。Priorities 为 HIGH 由于我是一个detector检测两个错，我DIY了 CASE 2 来验证。

在Github上 `BIT_AND_ZZ`的样例都需要知道变量的具体值为0，我们无法实现。具体实现过程类似第一个 

#### UPDATE VA_FORMAT_STRING_USES_NEWLINE

**效果**

1. 修复了 `\\n` 的false positive.
2. 增加了 Formatter, PrintStream, Writer流的检测 （仅匹配关键词，调低了bug等级）

**Regex**

```
(?:(?:(([F,f]ormatter)|([P,p]rintStream)|([W,w]riter))\.format))\([\w\.\s\(\)]*,{0,1}\s*\"([^\"]*)\"\s*
```

**Examples**

```Java
public static void main(String[] args) throws IOException {
        Formatter formatter = new Formatter();
        File file = new File("test.txt");
        File file2 = new File("test2.txt");
        PrintStream printStream = new PrintStream(new FileOutputStream(file,true),true,"UTF-8");
        PrintWriter printWriter = new PrintWriter(file2,"UTF-8");
        System.out.printf("|%-6s|%-12s|%-12s|\\n", "№ з/п", "Вхідний бал", "Результат округлення");
        printWriter.printf("This is the %s bug\n","first");
        printWriter.format("This is not a bug");
        try{
            int c = 4/0;
            System.out.println("c=" + c);
        }catch(Exception e){
            printStream.printf("This is the %d bug\n",2);
            printStream.format("This is the %d bug\n",3);
            e.printStackTrace(printStream);
        }
        formatter.format("This is the %d bug\n",4);
        String str = formatter.toString();
        System.out.println(str);
        printStream.close();
        printWriter.close();
      
    }
```

**实现思路**

[Spotbugs实现](https://github.com/spotbugs/spotbugs/blob/07bf864b83083c467e29f1b2de58a2cf5aa5c0d6/spotbugs/src/main/java/edu/umd/cs/findbugs/detect/FormatStringChecker.java#L107-L113)
- java.util.Formatter#format()
	- format(Locale l, String format, Object... args)
	- format(String format, Object... args)
- java.lang.String#format()
	- format(Locale l, String format, Object... args)
	- format(String format, Object... args)
- java.io.PrintStream#format()
	- format(Locale l, String format, Object... args)
	- format(String format, Object... args)
- java.io.PrintStream#printf()
	- printf(Locale l, String format, Object... args)
	- printf(String format, Object... args)
- \*\*Writer#format()
- \*\*Writer#printf()
- \*\*Logger#fmt()


如果出现printf，则根据原来的pattern检测，断定是VA_FORMAT_STRING_USES_NEWLINE

如果出现了 formatter/printStream/Writer.format 的字样，则进入 relax_p （松弛条件）。由于部分变量的命名会和类型有关， 比如PrintStream 可能会命名为 xxprintStream. 通过匹配类似的变量名，来检测这个pattern。 这个pattern的等级为  Priorities.EXP_PRIORITY 。最后提示 If java/util/Formatter class, java/io/PrintStream class or java/io/Writer class was used, format string should use %n rather than \\n. Otherwise, ignore this bug. 让用户自己去检查是否使用了这些类。

针对于false positive 用如下语句检测。

```python
for i in range(len(format_str)):
	if format_str[i] == '\\' and i + 1 < len(format_str) and format_str[i+1] == 'n'and (i==0 or (i-1>=0 and format_str[i-1] != 		'\\')):
    idx_list.append(i)
```

idx_list 找到所有 \n的位置， 且\n之前没有\ （去掉false positive）
