## Nm: Class defines hashcode(); should it be hashCode()? (NM_LCASE_HASHCODE)

### Regex

```regexp
((public|protected)\s+)*int\s+hashcode\(
```

### Example

```java
int hashcode()
public int hashcode()
protected int hashcode()
```

### 实现思路

[spotbugs 实现](https://github.com/spotbugs/spotbugs/blob/a6f9acb2932b54f5b70ea8bc206afb552321a222/spotbugs/src/main/java/edu/umd/cs/findbugs/detect/Naming.java#L561):

1. 匹配方法名是否为hashcode, Signature 是否为`()I`
2. 该方法访问修饰符不为`private`



## Nm: Class defines tostring(); should it be toString()? (NM_LCASE_TOSTRING)

### Regex

```regexp
((public|protected)\s+)*String\s+tostring\(
```

### Example

```java
String tostring()
public String tostring()
protected String tostring()
```

### 实现思路

[spotbugs 实现](https://github.com/spotbugs/spotbugs/blob/a6f9acb2932b54f5b70ea8bc206afb552321a222/spotbugs/src/main/java/edu/umd/cs/findbugs/detect/Naming.java#L561):

1. 匹配方法名是否为tostring, Signature 是否为`()Ljava/lang/String;`
2. 该方法访问修饰符不为`private`



