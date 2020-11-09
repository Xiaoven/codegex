import pytest

from patterns.detect.find_ref_comparison import FindRefComparison
from rparser import parse

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
        WebView gv = new WebView(context);''', 0, 5),
    # From spotBugs: https://github.com/spotbugs/spotbugs/blob/3883a7b750fb339577be073bc45e36b6f268777b/spotbugsTestCases/src/java/sfBugs/Bug2912638.java
    (FindRefComparison(), 'ES_COMPARING_STRINGS_WITH_EQ', 'Fake.java',
     '''@@ -20,11 +19,11 @@ protected static void findBugsTest(Bug2912638 person) {
                 String value = person.getName();

                 if ("FOO" == value)
                     System.out.println("a");
                 else
                     System.out.println("a3");
                 if (value == "FOO")
                     System.out.println("a");
                 else
                     System.out.println("a3");
             }''', 2, 21),
    # https://github.com/rxp90/jsymspell/pull/3/files?file-filters%5B%5D=.java#diff-423e657b915a047bfecd389dcc05d1f71336871ed156c158b730f3bb6c35d15fR42
    (FindRefComparison(), 'ES_COMPARING_STRINGS_WITH_EQ', 'Fake.java',
     '''@@ -20,1 +19,1 @@
            "abcd == abcde - {e} (distance 1), abcd == abcdef - {ef} (distance 2)"''', 0, 19),
    # https://github.com/hornstein/boardcad-java/pull/5/files#diff-7e74924bbc85100b71c52a1f86b2f7053fdf3474c989e53f27854651d49d359eR674
    (FindRefComparison(), 'ES_COMPARING_STRINGS_WITH_EQ', 'Fake.java',
     '''@@ -1,1 +1,1 @@
     if (string.startsWith("(cp") == false)''', 0, 1),
    # https://github.com/VikaAdamovska/java-elementary-lesson25-spring-web/pull/1/files#diff-afa4c3044f61274747787df8b223c11d9be17cb312d506ba52b23349da7e9a99R22
    (FindRefComparison(), 'ES_COMPARING_STRINGS_WITH_EQ', 'Fake.java',
     '''@@ -0,0 +1,1 @@
     childLogger.info("INFO == INFO");''', 0, 1),

    # DIY
    (FindRefComparison(), 'EC_NULL_ARG', 'Bug2912638.java',
     '''@@ -20,2 +19,2 @@ private static Object toJavaObject(Object maybeJson) throws JSONException{
                if (maybeJson == null || maybeJson.equals(null))
                     return null;
             }''', 1, 19),

    # From other repository: https://github.com/aljohn368/first/commit/22c43eba4c4bb08e456b46d27695ff604e726d71
    (FindRefComparison(), 'RC_REF_COMPARISON_BAD_PRACTICE_BOOLEAN', 'ShadePluginDetector.java',
     "@@ -62,8 +62,8 @@ private boolean calculateValue() {\n"
     "         if (PluginPropertyUtils.getPluginVersion(nbmp.getMavenProject(), Constants.GROUP_APACHE_PLUGINS, \"maven-shade-plugin\") == null) {\n"
     "             return true;\n"
     "         }\n"
     "+        Boolean toret = Boolean.valueOf(PluginPropertyUtils.getPluginProperty(project, Constants.GROUP_APACHE_PLUGINS, \"maven-shade-plugin\", \"shadedArtifactAttached\", \"shade\", null));\n"
     "+        if (toret == Boolean.FALSE) {\n"
     "             if (pr != null) {\n"
     "                 pr.addReport(PROBLEM_REPORT);\n"
     "             }", 1, 66),
]


@pytest.mark.parametrize('detector,pattern_type,file_name,patch_str,expected_length,line_no', params)
def test(detector, pattern_type: str, file_name: str, patch_str: str, expected_length: int, line_no: int):
    patch = parse(patch_str)
    patch.name = file_name

    detector.visit([patch])
    if expected_length > 0:
        assert len(detector.bug_accumulator) == expected_length
        assert detector.bug_accumulator[0].line_no == line_no
        assert detector.bug_accumulator[0].type == pattern_type
    else:
        assert len(detector.bug_accumulator) == 0
