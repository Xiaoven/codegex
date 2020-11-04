import pytest

from patterns.detect.find_ref_comparison import FindRefComparison
from rparser import Patch



class TestSerializableIdiom:
    # From other repository: https://github.com/aljohn368/first/commit/22c43eba4c4bb08e456b46d27695ff604e726d71
    def test_RC_REF_COMPARISON_BAD_PRACTICE_BOOLEAN_01(self):
        patch = Patch()
        patch.name = "ShadePluginDetector.java"
        patch.parse("@@ -62,8 +62,8 @@ private boolean calculateValue() {\n"
                    "         if (PluginPropertyUtils.getPluginVersion(nbmp.getMavenProject(), Constants.GROUP_APACHE_PLUGINS, \"maven-shade-plugin\") == null) {\n"
                    "             return true;\n"
                    "         }\n"
                    "+        Boolean toret = Boolean.valueOf(PluginPropertyUtils.getPluginProperty(project, Constants.GROUP_APACHE_PLUGINS, \"maven-shade-plugin\", \"shadedArtifactAttached\", \"shade\", null));\n"
                    "+        if (toret == Boolean.FALSE) {\n"
                    "             if (pr != null) {\n"
                    "                 pr.addReport(PROBLEM_REPORT);\n"
                    "             }")
        detector = FindRefComparison()
        detector.visit([patch])
        detector.report()
        assert len(detector.bug_accumulator) == 1
        bugins = detector.bug_accumulator[0]
        assert bugins.line_no == 66

    # From spotBugs: https://github.com/spotbugs/spotbugs/blob/3883a7b750fb339577be073bc45e36b6f268777b/spotbugsTestCases/src/java/sfBugs/Bug2912638.java
    def test_ES_COMPARING_STRINGS_WITH_EQ_01(self):
        patch = Patch()
        patch.name = "Bug2912638.java"
        patch.parse('''@@ -20,11 +19,11 @@ protected static void findBugsTest(Bug2912638 person) {
            String value = person.getName();
    
            if ("FOO" == value)
                System.out.println("a");
            else
                System.out.println("a3");
            if (value == "FOO")
                System.out.println("a");
            else
                System.out.println("a3");
        }''')
        detector = FindRefComparison()
        detector.visit([patch])
        detector.report()
        assert len(detector.bug_accumulator) == 2
        assert detector.bug_accumulator[0].line_no == 21
        assert detector.bug_accumulator[1].line_no == 25

    # DIY
    def test_EC_NULL_ARG_01(self):
        patch = Patch()
        patch.name = "test.java"
        patch.parse('''@@ -20,2 +19,2 @@ private static Object toJavaObject(Object maybeJson) throws JSONException{
           if (maybeJson == null || maybeJson.equals(null))
                return null;
        }''')
        detector = FindRefComparison()
        detector.visit([patch])
        detector.report()
        assert len(detector.bug_accumulator) == 1
        assert detector.bug_accumulator[0].line_no == 19


params = [
    (FindRefComparison(), 'ES_COMPARING_STRINGS_WITH_EQ', 'Fake.java',
     '''@@ -1,0 +1,0 @@
     @Override
    public void onReceive(final Context context, Intent intent) {
       /*  dbhelper = new DatabaseHandler(context, "RG", null, 1);
        mURL = dbhelper.Obt_url();
        if (mURL == ""){  
            mURL = "http://186.96.89.66:9090/crccoding/f?p=2560:9999";
            Log.i("SQLL","Url vacio");
        }else{
            Log.i("SQLL","Url cargado   "+mURL);
        }*/
        WebView gv = new WebView(context);''', 0, 5)
]

@pytest.mark.parametrize('detector,pattern_type,file_name,patch_str,expected_length,line_no', params)
def test(detector, pattern_type:str, file_name: str, patch_str: str, expected_length: int, line_no: int):
    patch = Patch()
    patch.name = file_name
    patch.parse(patch_str)
    detector.visit([patch])
    if expected_length > 0:
        assert len(detector.bug_accumulator) == expected_length
        assert detector.bug_accumulator[0].line_no == line_no
        assert detector.bug_accumulator[0].type == pattern_type
    else:
        assert len(detector.bug_accumulator) == 0