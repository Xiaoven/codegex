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

1. 匹配方法名是否为hashcode, signature是否为`"()I"`
2. 该方法不为`private`

