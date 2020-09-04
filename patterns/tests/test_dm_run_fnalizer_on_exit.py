from rparser import Patch
from patterns.detect.dumb_methods import DmRunFinalizerOnExit


class TestImseDontCatchImse:
    def test_01(self):
        patch = Patch()
        patch.name = "StdEntropyDecoder.java"
        patch.parse("@@ -622,7 +622,7 @@ public StdEntropyDecoder(CodedCBlkDataSrcDec src, DecoderSpecs decSpec,\n         if (DO_TIMING) {\n             time = new long[src.getNumComps()];\n             // If we are timing make sure that 'finalize' gets called.\n+            System.runFinalizersOnExit(true);\n         }\n \n         // Initialize internal variables")
        detector = DmRunFinalizerOnExit()
        detector.visit([patch])
        assert len(detector.bug_accumulator) == 1
