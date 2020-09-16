STCAL: Static DateFormat （STCAL_STATIC_SIMPLE_DATE_FORMAT_INSTANCE）

Regex
static\s*.*\s*SimpleDateFormat\s*.*\s*=\s*new\s*SimpleDateFormat\(

Examples
public static final SimpleDateFormat PRV_ST_FI_LOCAL_SIMPLE_DATE_FORMAT = new SimpleDateFormat();



实现思路
检测是否有static XXX SimpleDateFormat XXX = new SimpleDateFormat(  出现