from rparser import Patch
from patterns.detect.static_calendar_detector import StaticCalendarDetector

class TestStcalStaticSimpleDateFormatInstance:

    # From spotBugs: https://github.com/spotbugs/spotbugs/blob/3883a7b750fb339577be073bc45e36b6f268777b/spotbugsTestCases/src/java/sfBugs/Bug3441912.java
    def test_STCAL_STATIC_SIMPLE_DATE_FORMAT_INSTANCE_01(self):
        patch = Patch()
        patch.name = "Bug3441912.java"
        patch.parse('''@@ -0,0 +1,34 @@
        import java.text.DateFormat;
        import java.text.SimpleDateFormat;
        
        public class Main{
            public static final SimpleDateFormat FORMAT_DB_DATE = new SimpleDateFormat("yyyyMMdd");
            public static final DateFormat FORMAT_DB_DATE2 = new SimpleDateFormat("yyyyMMdd");
            public static  DateFormat formatDBDate3;
        }''')
        detector = StaticCalendarDetector()
        detector.visit([patch])
        assert len(detector.bug_accumulator) == 3
