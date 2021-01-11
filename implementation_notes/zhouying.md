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

