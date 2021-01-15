## Nm: Class defines hashcode(); should it be hashCode()? (NM_LCASE_HASHCODE)

如果方法名为 `hashCode`, 但不符合 `public int hashCode()` 的话，会 build failed


### Regex

```regexp
^[\w\s]*?\bint\s+hashcode\s*\(\s*\)
```

### Example

```java
int hashcode()
public int hashcode()
protected int hashcode()
public final int hashcode(){
	     int hashcode(){
```

### 实现思路

[spotbugs 实现](https://github.com/spotbugs/spotbugs/blob/a6f9acb2932b54f5b70ea8bc206afb552321a222/spotbugs/src/main/java/edu/umd/cs/findbugs/detect/Naming.java#L561):

1. 匹配方法名是否为hashcode, signature是否为`"()I"`， 即参数列表为空，返回值为 int
2. 该方法不为`private`


## Nm: Class defines tostring(); should it be toString()? (NM_LCASE_TOSTRING)

### Regex

```regexp
^[\w\s]*?\bString\s+tostring\s*\(\s*\)
```

### Example

```java
String tostring()
public String tostring()
protected String tostring()
public static final String tostring(){
```

### 实现思路

[spotbugs 实现](https://github.com/spotbugs/spotbugs/blob/a6f9acb2932b54f5b70ea8bc206afb552321a222/spotbugs/src/main/java/edu/umd/cs/findbugs/detect/Naming.java#L561):

1. 匹配方法名是否为tostring, Signature 是否为`()Ljava/lang/String;`
2. 该方法访问修饰符不为`private`

## FE: Doomed test for equality to NaN (FE_TEST_IF_EQUAL_TO_NOT_A_NUMBER)

### Regex

```regexp
((?:(?P<aux1>\((?:[^()]++|(?&aux1))*\))|[\w."])++)\s*[!=]=\s*((?:(?&aux1)|[\w."])+)
```

refers to **ES: Comparison of String objects using == or != (ES_COMPARING_STRINGS_WITH_EQ)**

### Example

```java
x == Double.NaN
```

[**SpotBugs 实现思路**](https://github.com/spotbugs/spotbugs/blob/a6f9acb2932b54f5b70ea8bc206afb552321a222/spotbugs/src/main/java/edu/umd/cs/findbugs/detect/FindFloatEquality.java#L131)

因为jdk1.8+编译器已经优化number comparison，即与Double.NaN(Float.NaN)比较都被编译成False，所以无需spotbugs检查出类似错误。

1. 匹配'>', '<', '>=', '<=', '==', '!='
2. 提取运算数
3. 判断是否有且仅有一个运算数为Double.NaN(Float.NaN)，即两个运算数都为则不报该warning

## BC: Impossible downcast of toArray() result (BC_IMPOSSIBLE_DOWNCAST_OF_TOARRAY)

### Regex

```regexp
\(\s*(\w+)\s*\[\s*\]\s*\)\s*((?:(?P<aux1>\((?:[^()]++|(?&aux1))*\))|[\w.$<>\s])+?)\s*\.\s*toArray\s*\(\s*\)
```

### Example

```java
(String[]) c.toArray();
(String[][])new LinkedList<String>().toArray();
```

### 实现思路

[**SpotBugs实现思路**](https://github.com/spotbugs/spotbugs/blob/a6f9acb2932b54f5b70ea8bc206afb552321a222/spotbugs/src/main/java/edu/umd/cs/findbugs/detect/FindBadCast2.java#L612)

我的思路：

1. 提取强制转换类型和 `.toArray` 前面的 object name
2. 如果强制转换类型不为 `Object[]` 且 obejct name 不包含 `Arrays.asList`，则报 warning