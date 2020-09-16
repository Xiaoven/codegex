from patterns.detect.find_ref_comparison import FindRefComparison
from rparser import Patch



class TestSerializableIdiom:
    def test(self):
        patch = Patch()
        # patch from https://github.com/aljohn368/first/commit/22c43eba4c4bb08e456b46d27695ff604e726d71
        patch.name = "maven/src/org/netbeans/modules/maven/queries/ShadePluginDetector.java"
        patch.parse("@@ -62,8 +62,8 @@ private boolean calculateValue() {\n         if (PluginPropertyUtils.getPluginVersion(nbmp.getMavenProject(), Constants.GROUP_APACHE_PLUGINS, \"maven-shade-plugin\") == null) {\n             return true;\n         }\n+        Boolean toret = Boolean.valueOf(PluginPropertyUtils.getPluginProperty(project, Constants.GROUP_APACHE_PLUGINS, \"maven-shade-plugin\", \"shadedArtifactAttached\", \"shade\", null));\n+        if (toret == Boolean.FALSE) {\n-        boolean toret = Boolean.parseBoolean(PluginPropertyUtils.getPluginProperty(project, Constants.GROUP_APACHE_PLUGINS, \"maven-shade-plugin\", \"shadedArtifactAttached\", \"shade\", null));\n-        if (!toret) {\n             if (pr != null) {\n                 pr.addReport(PROBLEM_REPORT);\n             }")
        detector = FindRefComparison()
        detector.visit([patch])
        detector.report()
        assert len(detector.bug_accumulator) == 1
