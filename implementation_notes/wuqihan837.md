STCAL: Static DateFormat （STCAL_STATIC_SIMPLE_DATE_FORMAT_INSTANCE）
Regex
static\s*.\s(SimpleDateFormat|DateFormat|MyOwnDateFormat)
Examples
①public static final SimpleDateFormat PRV_ST_FI_LOCAL_SIMPLE_DATE_FORMAT = new SimpleDateFormat(); ②static DateFormat; ③static DateFormat = null; ④static MyOwnDateFormat = new MyOwnDateFormat();
实现思路 DateFormat和SimpleDateFormat这些类是非线程安全的，不宜和static一起使用
无论是否有'=' 或者 'new 类名()' 该正则表达式都可以匹配到该pattern Example①： 匹配到static final SimpleDateFormat PRV_ST_FI_LOCAL_SIMPLE_DATE_FORMAT = new SimpleDateFormat() Example②：匹配到static DateFormat Example③：匹配到static DateFormat Example④：匹配到static MyOwnDateFormat = new MyOwnDateFormat()