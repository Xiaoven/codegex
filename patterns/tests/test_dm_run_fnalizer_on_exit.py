from patterns.detect.find_finalize_invocations import FiExplicitInvocation
from rparser import Patch
from patterns.detect.dumb_methods import DmRunFinalizerOnExit


class TestFinalizer:
    def test_DmRunFinalizerOnExit(self):
        patch = Patch()
        patch.name = "StdEntropyDecoder.java"
        patch.parse("@@ -622,7 +622,7 @@ public StdEntropyDecoder(CodedCBlkDataSrcDec src, DecoderSpecs decSpec,\n         if (DO_TIMING) {\n             time = new long[src.getNumComps()];\n             // If we are timing make sure that 'finalize' gets called.\n+            System.runFinalizersOnExit(true);\n         }\n \n         // Initialize internal variables")
        detector = DmRunFinalizerOnExit()
        detector.visit([patch])
        assert len(detector.bug_accumulator) == 1

    def test_FiExplicitInvocation(self):
        patch = Patch()
        patch.name = "Fake.java"
        patch.parse("@@ -622,7 +622,7 @@ public class Main extends Object{\n    void test() throws Throwable {\n        Object s = new Object();\n        this.finalize();\n    }\n}");
        detector = FiExplicitInvocation()
        detector.visit([patch])
        detector.report()
        assert len(detector.bug_accumulator) == 1
