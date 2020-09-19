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