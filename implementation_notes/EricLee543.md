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

注： DIY的testcase 不会在IDEA的spotbugs中报错，但我们采用的是一种粗略的实现方式。在我们这里是被认为是会出现bug的。 （bug的prioritiy最低）

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

DIY的testcase都会被spotbugs报错



#### DLS: **Useless** **increment** **in** **return** **statement**

**Regex**

`return\s+[A-Za-z_\$][A-Za-z_\$0-9]*(\+\+|\-\-)\s*;`

**Examples**

```java
 CASE1 
 public int getIntMinus1Bad(String intStr) {
             int i = Integer.parseInt(intStr);
             return i--;
  }
  // 这个是SpotBugs的样例，此外没找到别的样例了
CASE 2 
     public class Main{
           static int nextNumber(int i){\n      
                return primes[i]++;
                                       }
     }
  // 半DIY 这个样例是GitHub其他repo里的代码，仓库拥有者说这是一个DLS_DEAD_LOCAL_INCREMENT_IN_RETURN。但我在IDEA的spotbug 插件中跑不出来。我认为此处如果是一个数组元素的话有确定意义，会在语句结束后自增。因而不应该被检测出来

CASE 3
 public class Main{
           static int nextNumber(int $num123){\n      
                return $num123++;
                                       }
     }
//DIY 增加一个++的样例，以及变成一个多字母复杂的变量
```

##### 实现思路

这个pattern为了检测在 return语句中无用的增量。尤其是后缀的++/--。DLS这一类pattern都是针对局部变量（L就是local的意思）。局部变量不涉及方法，因而不需要判断（）。 如果返回的是一个等式，例如`y+(x++)`我在spotbug插件上测试，是不会被检测为Useless increment in return statement的。

总之就是 return 变量++； 匹配这个模式即可。 变量可以由\$或者\_或者字母开头，于是采用[A-Za-z_\$]为开头，除了变量名首个字符，之后的字符可以是数字，顺理成章的加上0-9。最后匹配一个++/--