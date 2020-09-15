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