from patterns.detect.serializable_idiom import SerializableIdiom
from rparser import Patch



class TestSerializableIdiom:
    def test_SE_NONSTATIC_SERIALVERSIONID(self):
        patch = Patch()
        patch.name = "Fake.java"
        patch.parse("@@ -1,3 +1,1 @@ public class Main{\n+    final long serialVersionUID = 10000L;\n}")
        detector = SerializableIdiom()
        detector.visit([patch])
        detector.report()
        assert len(detector.bug_accumulator) == 1

    def test_SE_NONFinal_SERIALVERSIONID(self):
        patch = Patch()
        patch.name = "Fake.java"
        patch.parse("@@ -1,3 +1,1 @@ public class Main{\n+    static long serialVersionUID = 10000L;\n}")
        detector = SerializableIdiom()
        detector.visit([patch])
        detector.report()
        assert len(detector.bug_accumulator) == 1

    def test_SE_NONLong_SERIALVERSIONID(self):
        patch = Patch()
        patch.name = "Fake.java"
        patch.parse("@@ -1,3 +1,1 @@ public class Main{\n+    static final int serialVersionUID = 10000L;\n}")
        detector = SerializableIdiom()
        detector.visit([patch])
        detector.report()
        assert len(detector.bug_accumulator) == 1