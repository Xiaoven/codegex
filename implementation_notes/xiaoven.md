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