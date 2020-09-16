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