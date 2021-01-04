## FS: Format string should use %n rather than n (VA_FORMAT_STRING_USES_NEWLINE)

### Regex
```regexp
(?:(?:String\.format)|printf)\([\w.\s()]*,?\s*"([^"]*)"\s*
```
### Examples
```java

String.format( Locale.US , "Payload:\n%s" , new Object[1]);

String.format("Payload:\n%s" , new Object[1]);
```

### 实现思路

[SpotBugs](https://github.com/spotbugs/spotbugs/blob/07bf864b83083c467e29f1b2de58a2cf5aa5c0d6/spotbugs/src/main/java/edu/umd/cs/findbugs/detect/FormatStringChecker.java#L107-L113)

- java.util.Formatter.format()
- java.lang.String.format()
- *Writer.format()
- java.io.PrintStream.format()
- java.io.PrintStream.printf()
- \*Writer.printf()
- \*Logger.fmt()

1. 提取 `String.format(Locale l, String format, Object... args)`  和 `String.format(String format, Object... args)` 调用中的 format 部分

2. 检查 format 部分是否包含 `\n` 字符



## DMI: Random object created and used only once (DMI_RANDOM_USED_ONLY_ONCE)
### Regex
```regexp
new\s+[\w\.]*Random(?:(?P<aux1>\((?:[^()]++|(?&aux1))*\)))++\.next\w*\(\s*\)
```
### Examples
```java
// https://github.com/jenkinsci/android-emulator-plugin/commit/0e104f3f0fc18505c13932fccd3b2297e78db694#diff-238b9af87181bb379670392cdb1dcd6bL173
seedValue = new Random().nextLong();
// https://github.com/adaptris/interlok/commit/8dd32e9b89a4b17662faa7ca986756f3cc348cc7#diff-1e0469ce35c1d148418525088df452a2L405
pool.setTimeBetweenEvictionRunsMillis(threadLifetimeMs() + new Random(threadLifetimeMs()).nextLong());
// https://github.com/adaptris/interlok/commit/8dd32e9b89a4b17662faa7ca986756f3cc348cc7#diff-766b5e25592ad321e107f1f856d8a08bL102
pool.setTimeBetweenEvictionRunsMillis(EVICT_RUN + new Random(EVICT_RUN).nextLong());
// DIY
seedValue = new java.util.Random().nextLong();
```
### 实现思路
[spotbugs 实现](https://github.com/spotbugs/spotbugs/blob/07bf864b83083c467e29f1b2de58a2cf5aa5c0d6/spotbugs/src/main/java/edu/umd/cs/findbugs/detect/DumbMethods.java#L495): 判断变量类型，其中freshRandomOnTos和freshRandomOneBelowTos两个变量意思不明。

根据[搜到的例子](https://github.com/search?q=DMI_RANDOM_USED_ONLY_ONCE&type=commits)，可以匹配形如 `new java.util.Random(XXX).nextXXX()` 的用法，它创建对象后马上使用，而不是把对象存在变量里，方便复用

##DMI: Don’t use removeAll to clear a collection (DMI_USING_REMOVEALL_TO_CLEAR_COLLECTION)
检测形如 c.removeAll(c) 的pattern

### Regex

```regexp
(.*)\.removeAll\((.*)\)
```
### Examples
```java
c.removeAll(c)
```
### 实现思路
[spotbugs 实现](https://github.com/spotbugs/spotbugs/blob/07bf864b83083c467e29f1b2de58a2cf5aa5c0d6/spotbugs/src/main/java/edu/umd/cs/findbugs/detect/FindUnrelatedTypesInGenericContainer.java#L509)

1. 判断 object 和传参是否相等
2. 如是，再判断 method name 是否是 `removeAll`

## ES: Comparison of String objects using == or != (ES_COMPARING_STRINGS_WITH_EQ)
如题，unless both strings are either constants in a source file, or have been interned using the String.intern() method
### Regex
```regexp
((?:(?P<aux1>\((?:[^()]++|(?&aux1))*\))|[\w."])++)\s*[!=]=\s*((?:(?&aux1)|[\w."])+)
```
### Examples
```java
if ("FOO" == value)
```
### 实现思路
[spotbugs 实现](https://github.com/spotbugs/spotbugs/blob/07bf864b83083c467e29f1b2de58a2cf5aa5c0d6/spotbugs/src/main/java/edu/umd/cs/findbugs/detect/FindRefComparison.java#L996) 

由于我们无法获得变量类型等信息，故提取 `op_1 == op_2` 中的 `op_1` 和 `op_2`。如果其中一个是带双引号的string constant，另一个既不是string constant，也不以 `String.intern` 开头，则判断它为 ES_COMPARING_STRINGS_WITH_EQ

## UI: Usage of GetResource may be unsafe if class is extended (UI_INHERITANCE_UNSAFE_GETRESOURCE)

### Regex
```regexp
(\w*)\.*getClass\(\s*\)\.getResource(?:AsStream){0,1}\(
```
### Examples
```java
getClass().getResourceAsStream("XStreamDOMTest.data1.xml")
this.getClass().getResourceAsStream(DB_SCHEMA)
URL url = this.getClass().getResource(imagePath)
```
### 实现思路
[spotbugs](https://github.com/spotbugs/spotbugs/blob/07bf864b83083c467e29f1b2de58a2cf5aa5c0d6/spotbugs/src/main/java/edu/umd/cs/findbugs/detect/InheritanceUnsafeGetResource.java#L108)

我的思路：提取 `this.getClass().getResource(...)` 里 `this` 位置的内容，如果为 None 或 this， 则生成 warning

## Nm: Class names shouldn’t shadow simple name of superclass (NM_SAME_SIMPLE_NAME_AS_SUPERCLASS)
Java 编译规则：

1. class只能继承一个父类，但可以实现多个接口
2. extends 在 implements 之前 

### Regex
```regexp
class\s+([\w$]+)\s*(?P<gen><(?:[^<>]++|(?&gen))*>)?\s+extends\s+([\w$.]+)
```
### Examples
```java
public class SpringLiquibase extends liquibase.integration.spring.SpringLiquibase
public class Future<V> extends io.netty.util.concurrent.Future<V>
```
### 实现思路
[spotbugs 实现](https://github.com/spotbugs/spotbugs/blob/07bf864b83083c467e29f1b2de58a2cf5aa5c0d6/spotbugs/src/main/java/edu/umd/cs/findbugs/detect/Naming.java#L308) 

1. 提取 class name 和 superclass name，默认 class name 是 simple name
2. 假如 superclass name 是 qualified name，则从中提取 simple name
3. 判断两者是否相等。

## Nm: Class names shouldn’t shadow simple name of implemented interface (NM_SAME_SIMPLE_NAME_AS_INTERFACE)
Java 编译规则： 

1. interface 可以 `extends` 多个 interfaces
2. interface 定义不能有 implements 语句

### Regex
有两种情况：
1. class 定义里的 implements 部分
2. interface 定义里的 extends 部分

```regexp
class\s+([\w$]+)\b.*\bimplements\s+([^{]+)
interface\s+([\w$]+)\s*(?P<gen><(?:[^<>]++|(?&gen))*>)?\s+extends\s+([^{]+)
```
第二个正则表达式参考了 `((?!m).)*`， 表示匹配 `.` 的时候不包含
### Examples

```java
public class LocaleResolver implements org.springframework.web.servlet.LocaleResolver

public interface Future<V> extends io.netty.util.concurrent.Future<V> {

public class LocaleResolver implements DIY, org.springframework.web.servlet.LocaleResolver {

public class ALActivityImpl extends org.apache.shindig.social.core.model.ActivityImpl implements Activity
```
### 实现思路
[spotbugs 实现](https://github.com/spotbugs/spotbugs/blob/07bf864b83083c467e29f1b2de58a2cf5aa5c0d6/spotbugs/src/main/java/edu/umd/cs/findbugs/detect/Naming.java#L313) 类似 NM_SAME_SIMPLE_NAME_AS_SUPERCLASS

1. 提取 class/interface name 和 implements/extends 后的字符串
2. 将字符串 split 成 superclass/superinterface 的 simple name 列表
3. 判断列表中是否包含 class/interface name


## IL: A collection is added to itself (IL_CONTAINER_ADDED_TO_ITSELF)
As a result, computing the hashCode of this set will throw a StackOverflowException.
### Regex
```regexp
(.*)\.add\((.*)\)
```
不建议使用 `(\w*)\.add\(\1\)` 这样的写法，会少匹配。如 `bb.add(b)` 会匹配 `b.add(b)`
### Examples
```java
testee.add(testee)
```
### 实现思路
[spotbugs 实现](https://github.com/spotbugs/spotbugs/blob/07bf864b83083c467e29f1b2de58a2cf5aa5c0d6/spotbugs/src/main/java/edu/umd/cs/findbugs/detect/InfiniteRecursiveLoop.java#L104):
1. 检查 add 方法的 signature
2. 判断 stack 里的 object 和参数是否相等

我的做法：用正则匹配 `c.add(c)` 中 object 和参数位置，判断它们是否相等. 类似 DMI_USING_REMOVEALL_TO_CLEAR_COLLECTION.

## RV: Random value from 0 to 1 is coerced to the integer 0 (RV_01_TO_INT)
### Regex
```regexp
\(\s*int\s*\)\s*(\w+)\.(?:random|nextDouble|nextFloat)\(\s*\)
```
### Examples
```java
(int) Math.random()
(int) randomObject.nextDouble()
(int) randomObject.nextFloat()
```
### 实现思路
[spotbugs 实现](https://github.com/spotbugs/spotbugs/blob/07bf864b83083c467e29f1b2de58a2cf5aa5c0d6/spotbugs/src/main/java/edu/umd/cs/findbugs/detect/DumbMethods.java#L1144)
1. 首先要满足以下条件, 似乎是调用了 `Random.nextDouble` 或 `Math.random` 方法
```java
seen == Const.INVOKEVIRTUAL && "java/util/Random".equals(getClassConstantOperand())
&& "nextDouble".equals(getNameConstantOperand()) || seen == Const.INVOKESTATIC
&& ClassName.isMathClass(getClassConstantOperand()) && "random".equals(getNameConstantOperand())
```
2. 然后要满足 `seen == Const.D2I` ，其中 seen 是传入的参数，Const.D2I 是某个库定义的，应该是什么浮点数被 convert 成 integer 的意思

我的实现思路：
1. 匹配静态调用 `(int) Math.random()`
2. 匹配调用 `(int) randomObject.nextDouble()`， 并且拓展到 `nextFloat()` 方法。由于 randomObject 的名字可变，我们可以提取变量名，转成lowercase，看看是否包含 `rand`或者等于 `r`, 如果是，则 confidence 可以较高一点。


## Se: The readResolve method must be declared with a return type of Object. (SE_READ_RESOLVE_MUST_RETURN_OBJECT)

规范的定义为 `ANY-ACCESS-MODIFIER Object readResolve() throws ObjectStreamException`；与 SE_READ_RESOLVE_IS_STATIC 一起实现

### Regex
```regexp
((?:static|final|\s)*)\s+([^\s]+)\s+readResolve\s*\(\s*\)\s+throws\s+ObjectStreamException
```
### Examples
```java
Object readResolve() throws ObjectStreamException

public String readResolve() throws ObjectStreamException

static String readResolve() throws ObjectStreamException // 优先报返回值类型的 warning，而不报 static 的warning
```
### 实现思路
[Spotbugs](https://github.com/spotbugs/spotbugs/blob/07bf864b83083c467e29f1b2de58a2cf5aa5c0d6/spotbugs/src/main/java/edu/umd/cs/findbugs/detect/SerializableIdiom.java)
中的思路是先检测方法名是否为readResolve 且当前 class 是 serializable，如果是，则检查返回值类型是否是 `java.lang.Object` 类型，然后才
检测是否有static修饰词。

我的实现思路为：

1. 我们无法获取 class 是否是 serializable，故将默认 priority 从 high 降为 normal，且假设程序员只在 serializable class 中重写 readResolve 方法

2. 用 `([^\s]+)\s+readResolve` 提取返回值类型，判断是否为 `Object`

## EQ_COMPARING_CLASS_NAMES
错误原因：different classes with the same name if they are loaded by different class loader

### 例子
```java
if (auth.getClass().getName().equals(
    "complication.auth.DefaultAthenticationHandler")) {
```

```java
if (x.getClass().getName().equals(y.getClass().getName() )) {
```

### Spotbugs 实现思路
```java
if (callToInvoke(seen)) {
    equalsCalls++;
    checkForComparingClasses();
    if (AnalysisContext.currentAnalysisContext().isApplicationClass(getThisClass()) && dangerDanger) {
        bugReporter.reportBug(new BugInstance(this, "EQ_COMPARING_CLASS_NAMES", Priorities.NORMAL_PRIORITY)
                .addClassAndMethod(this).addSourceLine(this));
    }
}
```
没看懂，部分理解
1. callToInvoke(seen) 大概干了什么：
    - 检查是否是 equals 方法或类似 equals 的方法
        - 方法名的LowerCase是否包含 equals
        - 检查 signature, 即参数类型和返回值 (注意有两种用法)
            - o1.equals(o2)
            - Objects.equals(o1, o2)
2. checkForComparingClasses() 大概干了什么:
    - 好的 equals class 用法 (sawGoodEqualsClass = true):
        - o1.getClass() == o2.getClass()
        - xx.class == o2.getClass(), 且 xx.class 是 final class
    - 不好的用法 (sawBadEqualsClass = true)
        - xx.class == o2.getClass(), 但 xx.class 不是 final class: 报 EQ_GETCLASS_AND_CLASS_CONSTANT (Bad Practice)
    - 总的来说就是检查 EQ_GETCLASS_AND_CLASS_CONSTANT，给它调整 priority，并且设置两个成员变量 `sawGoodEqualsClass` 和 `sawBadEqualsClass` 的值
3. 要使得 dangerDanger 为 true，需要出现 `getName` 和 `getClass` 方法名
4. report bug 如果该 class 是 application class 且 danger 为 true

综上，首先检查是否调用了 equals 方法，然后检查 equals 方法要比较的两个对象是否调用了 `getClass().getName()`

### 我的实现思路
1. 当检查到 equals 方法时，提取它要比较的两个对象 (两种用法)
2. 判断两个参数是否有一个以 `getClass().getName()` 结尾
3. 提速: 只对同时包含 `equals`, `getClass` 和 `getName` 的语句进行正则匹配

### 正则
用来提取 equals 的比较对象，equals 前的不一定提取得完整，但至少可以保证可以完整提取到 `getClass().getName()`
```regexp
\b((?:[\w\.$"]|(?:\(\s*\)))+)\s*\.\s*equals(?P<aux1>\(((?:[^()]++|(?&aux1))*)\))
```

## DM_INVALID_MIN_MAX

Incorrect combination of Math.max and Math.min

### 例子
[spotbugs tests](https://github.com/spotbugs/spotbugs/blob/a6f9acb2932b54f5b70ea8bc206afb552321a222/spotbugsTestCases/src/java/sfBugsNew/Feature329.java)

```java
return Math.min(0, Math.max(100, rawInput));

return Math.max(Math.min(0, rawInput), 100);

int score = (totalCount == 0) ? 100 : (int) (100.0 * Math.max(1.0,
                Math.min(0.0, 1.0 - (scaleFactor * failCount) / totalCount)));
```

### spotbugs 实现
见 [InvalidMinMaxSubDetector](https://github.com/spotbugs/spotbugs/blob/d9557689c2a752a833eedf4eb5f37ee712a9c84f/spotbugs/src/main/java/edu/umd/cs/findbugs/detect/DumbMethods.java#L94)

初时，两成员变量 `upperBound = lowerBound = null`

1. 检查是否调用了 `Math.max` 或者 `Math.min` 方法。是则到下一步
2. 检查该方法的两个参数是否只有一个为 constant (数字)。 是则到下一步，否则两成员变量设为 null
3. 如果该方法名为 `min` ，则将 constant 赋值给成员变量 `upperBound` ，否则赋值给 `lowerBound`

接下来的部分不太理解，因为它似乎只对 `upperBound != null` 即外层是 `min` 成立。大概理解一下就好

4. 检查外层 min/max 函数的两个参数，是否只有一个是 method 类型，且也是 `Math.min` 或 `Math.max` 函数，如是则下一步
5. 如果 `lowerBound.compareTo(upperBound)` 结果大于 0, 则报该 bugs

我估计这个 subDetector 的 sawOpcode 方法应该是被调用了两次，才能给两个成员变量都赋上值。而且它从 stack 中读取的内容原本顺序应该也和我之前想的不一样，即先读取的是内层的 min/max，然后才是外层的 min/max，但是我不确定。

### 我的实现
1. 用正则提取第一个 `Math.min(...)` 或 `Math.max(...)` 的传参字符串 A
2. 再对传参字符串 A 应用上述正则，提取它的传参字符串 B
3. 将两个传参字符串的 `\s` 替换为空，然后根据 `,` split
4. 用强制转换成数字的办法，分别找出它们的参数中为 constant 的那个
5. 比较它们的大小