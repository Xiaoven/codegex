#### AM: Creates an empty zip file entry (AM_CREATES_EMPTY_ZIP_FILE_ENTRY)

##### Regex

```php
\.putNextEntry\(
\.closeEntry\(\s*\)   
```

##### Examples

```java
	  out.putNextEntry(feedbackSubAttachmentFolderEntry);
 -    out.flush();
 	  out.closeEntry(); 
```

##### 实现思路

1. 判断`putNextEntry（）`和`closeEntry（）`是否在相邻非空行



#### FI: Finalizer should be protected, not public (FI_PUBLIC_SHOULD_BE_PROTECTED)

##### Regex

```php
public\s+void\s+finalize\(\s*\) 
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

```php
new\s+String\s*\(\s*\)
```

##### Examples

```java
new String()
new String (  )
```

##### 实现思路

1. 直接搜索，注意空格



#### Dm: Method invokes inefficient new String(String) constructor (DM_STRING_CTOR)

##### Regex

```php
new\s+String\s*\(\s*(\w+|\")
```

##### Examples

```java
line = new String(loppedLine + nextLine);
return new String(s.substring(1, s.length() - 2));
String s = new String("") 
```

##### 实现思路

1. `new String`后的括号后只能是`"`或者是`\w`,因为无需提取括号里的内容，所以姑且这样匹配。