#### FS: Format string should use %n rather than n (VA_FORMAT_STRING_USES_NEWLINE)

##### Regex
```regexp
(?:(?:String\.format)|printf)\([\w\.\s\(\)]*,{0,1}\s*\"([^\"]*)\"\s*
```
##### Examples
printf("[WARN] Failed to set an integer 
    value of ")

String.format( Locale.US , "Payload:\n%s" , new Object[1]);

String.format("Payload:\n%s" , new Object[1]);

##### 实现思路

1. 提取 `String.format(Locale l, String format, Object... args)`  和 `String.format(String format, Object... args)` 调用中的 format 部分

2. 检查 format 部分是否包含 `\n` 字符



#### DMI: Random object created and used only once (DMI_RANDOM_USED_ONLY_ONCE)
##### Regex
```regexp
new\s+[\w\.]*Random(?:(?P<aux1>\((?:[^()]++|(?&aux1))*\)))++\.next\w*\(\s*\)
```
...
##### Examples
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
##### 实现思路
[spotbugs 实现](https://github.com/spotbugs/spotbugs/blob/07bf864b83083c467e29f1b2de58a2cf5aa5c0d6/spotbugs/src/main/java/edu/umd/cs/findbugs/detect/DumbMethods.java#L495): 判断变量类型，其中freshRandomOnTos和freshRandomOneBelowTos两个变量意思不明。

根据[搜到的例子](https://github.com/search?q=DMI_RANDOM_USED_ONLY_ONCE&type=commits)，可以匹配形如 `new java.util.Random(XXX).nextXXX()` 的用法，它创建对象后马上使用，而不是把对象存在变量里，方便复用

#### DMI: Don’t use removeAll to clear a collection (DMI_USING_REMOVEALL_TO_CLEAR_COLLECTION)
检测形如 c.removeAll(c) 的pattern

##### Regex

```regexp
(.*)\.removeAll\((.*)\)
```
##### Examples
```java
c.removeAll(c)
```
##### 实现思路
[spotbugs 实现](https://github.com/spotbugs/spotbugs/blob/07bf864b83083c467e29f1b2de58a2cf5aa5c0d6/spotbugs/src/main/java/edu/umd/cs/findbugs/detect/FindUnrelatedTypesInGenericContainer.java#L509)

1. 判断 object 和传参是否相等
2. 如是，再判断 method name 是否是 `removeAll`

#### ES: Comparison of String objects using == or != (ES_COMPARING_STRINGS_WITH_EQ)
如题，unless both strings are either constants in a source file, or have been interned using the String.intern() method
##### Regex
```regexp
((?:(?P<aux1>\((?:[^()]++|(?&aux1))*\))|[\w."])++)\s*[!=]=\s*((?:(?&aux1)|[\w."])+)
```
##### Examples
```java
if ("FOO" == value)
```
##### 实现思路
[spotbugs 实现](https://github.com/spotbugs/spotbugs/blob/07bf864b83083c467e29f1b2de58a2cf5aa5c0d6/spotbugs/src/main/java/edu/umd/cs/findbugs/detect/FindRefComparison.java#L996) 

由于我们无法获得变量类型等信息，故提取 `op_1 == op_2` 中的 `op_1` 和 `op_2`。如果其中一个是带双引号的string constant，另一个既不是string constant，也不以 `String.intern` 开头，则判断它为 ES_COMPARING_STRINGS_WITH_EQ
