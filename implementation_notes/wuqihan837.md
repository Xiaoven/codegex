#### STCAL: Static DateFormat（STCAL_STATIC_SIMPLE_DATE_FORMAT_INSTANCE）
[简要描述](https://spotbugs.readthedocs.io/en/stable/bugDescriptions.html#stcal-static-dateformat-stcal-static-simple-date-format-instance):
As the JavaDoc states, DateFormats are inherently unsafe for multithreaded use. 
##### Regex
```regexp
(\w*\s*)static\s+(?:final){0,1}\s*(DateFormat|SimpleDateFormat|Calendar|GregorianCalendar)\s+(\w*)
```
##### Examples
```java
static final SimpleDateFormat d;
static java.text.DateFormat d; 
static DateFormat d = null;
static SimpleDateFormat d = new SimpleDateFormat();
```
##### 实现思路
1. [spotbugs 实现思路](https://github.com/spotbugs/spotbugs/blob/07bf864b83083c467e29f1b2de58a2cf5aa5c0d6/spotbugs/src/main/java/edu/umd/cs/findbugs/detect/StaticCalendarDetector.java#L196): 
```java
/**
 * Checks if the visited field is of type {@link java.util.Calendar} or
 * {@link java.text.DateFormat} or a subclass of either one. If so and the
 * field is static and non-private it is suspicious and will be reported.
 */
```
2. 我的实现思路： 
	- 由于我们不方便获取变量类型信息，我们可以直接匹配 Field 的声明语句是否类似于 `public static DateFormat d`
	- 正则表达式会提取权限修饰符、类名和变量名，如果是 `private` field 则跳过，否则判断类名是 DateFormat 还是 Calendar
	- 根据 Javadoc , [DateFormat](https://docs.oracle.com/javase/8/docs/api/java/text/DateFormat.html) 的 Direct Known Subclasses 只有 `SimpleDateFormat` 类，故只匹配这两种类型，先不考虑自定义的 DateFormat 的子类; 同样，[Calendar](https://docs.oracle.com/javase/8/docs/api/java/util/Calendar.html) 的 Direct Known Subclasses 只有 `GregorianCalendar`.
#### STCAL: Static Calendar field (STCAL_STATIC_CALENDAR_INSTANCE)
##### Regex
```regexp
(\w*\s*)static\s*(?:final)?\s+(DateFormat|SimpleDateFormat|Calendar|GregorianCalendar)\s+(\w*)\s*[;=]
```
##### Examples
##### 实现思路
见 STCAL_STATIC_SIMPLE_DATE_FORMAT_INSTANCE

####  Se: The readResolve method must not be declared as a static method (SE_READ_RESOLVE_IS_STATIC)
简要描述：为使readResolve方法得到序列化机制的识别，不能作为一个静态方法来声明。

##### Regex
```regexp
(static)?\s*Object\s+readResolve\(\)\s+throws\s+ObjectStreamException
```
##### Examples
```java
private static Object readResolve() throws ObjectStreamException 
static Object readResolve() throws ObjectStreamException
public Object readResolve() throws ObjectStreamException  
```
##### 实现思路
Spotbugs中的思路是先检测方法名是否为readResolve，如果是，则继续检测是否有static修饰词，如果有，则触发该pattern。
#https://github.com/spotbugs/spotbugs/blob/07bf864b83083c467e29f1b2de58a2cf5aa5c0d6/spotbugs/src/main/java/edu/umd/cs/findbugs/detect/SerializableIdiom.java
我的实现思路为：将static用括号括起来，后面加？表示0次或者一次匹配。无论linecontent中是否有static，使用groups方法后得到的元组g长度都为1。
得到该元组后，if 'static' in g, 则说明有static，触发pattern。
