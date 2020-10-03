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
//https://github.com/spotbugs/spotbugs/blob/3883a7b750fb339577be073bc45e36b6f268777b/spotbugsTestCases/src/java/sfBugsNew/Bug1210.java
return Objects.equal(x, null);
//这里我不明白为啥spotbugs要用Google的库里的equal(Object,Object)函数，而不是文档里描述的equals(Object)，前者也是对后者的调用：    

//  public static boolean equal(@Nullable Object a, @Nullable Object b) {
//   return a == b || (a != null && a.equals(b));
//  }

//暂时只考虑spotbugs文档里说明的equals(null)的情况
```

##### 实现思路

[spotbugs 实现](https://github.com/spotbugs/spotbugs/blob/07bf864b83083c467e29f1b2de58a2cf5aa5c0d6/spotbugs/src/main/java/edu/umd/cs/findbugs/detect/FindRefComparison.java#L1127)

使用正则表达式可以直接判断`.equals()`和其中的`null`