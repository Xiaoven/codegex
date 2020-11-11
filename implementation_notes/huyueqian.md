#### FI: Finalizer should be protected, not public (FI_PUBLIC_SHOULD_BE_PROTECTED)

##### Regex

```regexp
public\s+void\s+finalize\s*\(\s*\) 
```

##### Examples

```java
@Override
public void finalize() throws LibvirtException {
```
##### 实现思路
1. 搜索finalize函数并判断是否为public（因为继承，返回类型只能是void，参数列表也相同，不能降低访问权所以不能是private）

#### Dm: Method invokes inefficient new String() constructor (DM_STRING_VOID_CTOR)
##### Regex
```regexp
new\s+String\s*(?P<aux1>\(((?:[^()]++|(?&aux1))*)\))
```
##### Examples
```java
new String()
new String (  )
```
##### 实现思路
- Spotbugs可以获取 String Constructor 的函数签名，从而知道参数类型，而我们不行。

- 该pattern可以直接匹配空参数，但为了和 DM_STRING_CTOR 整合，我们提取 `new String(param)` 中的 param 部分.
	- 如果 param 部分为 None 或者 param.strip() 为空字符串，则是 DM_STRING_VOID_CTOR;
	- 否则判断 param 部分是否包含 `"` 或 `+`，如是，则为 DM_STRING_CTOR. (无法获取变量类型，故只匹配明显为String的情况, 而 String 的 constructors 除了 `new String()` 和 `new String(String)` 外，参数都为数组，只有 String 类型的变量可以用 `+` 连接)

#### Dm: Method invokes inefficient new String(String) constructor (DM_STRING_CTOR)
##### Regex
```regexp
new\s+String\s*(?P<aux1>\(((?:[^()]++|(?&aux1))*)\))
```
##### Examples
```java
String s2 = new String("hh");
String s2 = new String(getStr() + "hh");
String s2 = new String(stringVar1 + stringVar2);
```
##### 实现思路
见 DM_STRING_VOID_CTOR.

### EC: Call to equals(null) (EC_NULL_ARG)

##### Regex

```regexp
(.*)\.equals\s*\(\s*null\s*\)
```

##### Examples

```java
//DIY
maybeJson.equals( null )
```

##### 实现思路

[spotbugs 实现](https://github.com/spotbugs/spotbugs/blob/07bf864b83083c467e29f1b2de58a2cf5aa5c0d6/spotbugs/src/main/java/edu/umd/cs/findbugs/detect/FindRefComparison.java#L1127)

使用正则表达式可以直接判断`.equals(null)`

### DMI: Vacuous call to collections (DMI_VACUOUS_SELF_COLLECTION_CALL)

##### Regex

```regexp
(.*)\.(?:contains|retain)All\((.*)\)
```

##### Examples

```java
//https://github.com/erzhen1379/hbase2.1.4/blob/fc65d24aa0043529f3d44ad4b6e50835b0beb056/hbase-common/src/test/java/org/apache/hadoop/hbase/util/TestConcatenatedLists.java#L129
  private void verify(ConcatenatedLists<Long> c, int last) {
    assertEquals((last == -1), c.isEmpty());
    assertEquals(last + 1, c.size());
    assertTrue(c.containsAll(c));
      
//DIY
  private void verify(ConcatenatedLists<Long> c, int last) {
    assertEquals((last == -1), c.isEmpty());
    assertEquals(last + 1, c.size());
    assertTrue(c.retainAll(c));
      
```

##### 实现思路

[spotbugs 实现](https://github.com/spotbugs/spotbugs/blob/07bf864b83083c467e29f1b2de58a2cf5aa5c0d6/spotbugs/src/main/java/edu/umd/cs/findbugs/detect/FindUnrelatedTypesInGenericContainer.java#L512)

spotbugs对于collection实例，先判断调用方法里的参数是否为实例本身，若是则再进一步判断方法类型以分类错误。用regex实现时，参照学姐的 DMI_USING_REMOVEALL_TO_CLEAR_COLLECTION，暂时不判断是否为collection。通过查阅collection的所有方法发现，此pattern只需实现`c.containsAll(c)`和`c.retainAll(c)`。

### DMI: Collections should not contain themselves (DMI_COLLECTIONS_SHOULD_NOT_CONTAIN_THEMSELVES)

##### Regex

```regexp
(.*)\.(?:contains|remove)\((.*)\)
```

##### Examples

```java
//https://github.com/josephearl/findbugs/blob/fd7ec8b5cc0b1b143589674cdcdb901fa5dc0dda/findbugsTestCases/src/java/gcUnrelatedTypes/Ideas_2011_06_30.java#L13
    @ExpectWarning("DMI_COLLECTIONS_SHOULD_NOT_CONTAIN_THEMSELVES")
    public static void testTP(Collection<Integer> c) {
        assertTrue(c.contains(c));
    }

//https://github.com/bndtools/bnd/commit/960664b12a8f8886779617a283883cdc901cef5e
    @ExpectWarning("DMI_COLLECTIONS_SHOULD_NOT_CONTAIN_THEMSELVES")
    public static void testTP(Collection<Integer> c) {
       return c.remove(c);
    }

```

##### 实现思路

[spotbugs 实现](https://github.com/spotbugs/spotbugs/blob/07bf864b83083c467e29f1b2de58a2cf5aa5c0d6/spotbugs/src/main/java/edu/umd/cs/findbugs/detect/FindUnrelatedTypesInGenericContainer.java#L506)

同上，参照学姐的 DMI_USING_REMOVEALL_TO_CLEAR_COLLECTION，暂时不判断是否为collection。通过查阅collection的所有方法发现，此pattern只需实现`s.contains(s)`和`s.remove(s)`。