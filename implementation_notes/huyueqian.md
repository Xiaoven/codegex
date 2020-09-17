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