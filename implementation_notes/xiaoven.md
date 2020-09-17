#### FS: Format string should use %n rather than n (VA_FORMAT_STRING_USES_NEWLINE)

##### Regex
(?:(?:String\.format)|printf)\([\w\.\s\(\)]*,{0,1}\s*\"([^\"]*)\"\s*

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
new\s+[\w\.]*Random(?:(?P<aux1>\((?:[^()]++|(?&aux1))*\)))++\.next\w*\(\s*\)
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
