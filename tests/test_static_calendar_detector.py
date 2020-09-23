from rparser import Patch
from patterns.detect.static_calendar_detector import StcalStaticSimpleDateFormatInstance


class TestStcalStaticSimpleDateFormatInstance:

    # From other repository:https://github.com/AngelZelayaAurea/my_test_repo/commit/0f334f79225b9bb00d3367405dd0c2fed4ae8585
    def test_STCAL_STATIC_SIMPLE_DATE_FORMAT_INSTANCE_01(self):
        patch = Patch()
        patch.name = "RuleStaticSimpleDateFormatInstanceLocalClass.java"
        patch.parse("@@ -0,0 +1,16 @@ \n+ package com.aurea.brpcs.ruletest.findbugs.compliant;\n+   \n+  import com.aurea.brpcs.ruletest.helpers.findbugs.DateFormat;\n+  import com.aurea.brpcs.ruletest.helpers.findbugs.SimpleDateFormat;\n+  \n+ public class RuleStaticSimpleDateFormatInstanceLocalClass {\n+  \n+ public static final DateFormat PRV_ST_FI_LOCAL_DATE_FORMAT = new SimpleDateFormat();\n+  \n+ protected static final DateFormat PRO_ST_FI_LOCAL_DATE_FORMAT = new SimpleDateFormat();\n+ \n+ public static final SimpleDateFormat PRV_ST_FI_LOCAL_SIMPLE_DATE_FORMAT = new SimpleDateFormat();\n+ \n+ protected static final SimpleDateFormat PRO_ST_FI_LOCAL_SIMPLE_DATE_FORMAT = new SimpleDateFormat();\n+ \n+ }\n")
        detector = StcalStaticSimpleDateFormatInstance()
        detector.visit([patch])
        assert len(detector.bug_accumulator) == 4
        detector.report()
