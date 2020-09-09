from patterns.detect.bit_signed_check import ChekBitSigned
from rparser import Patch

class TestChekSignOfBitoperation:
    def test_check_sign_of_bitoperation(self):
        patch = Patch()
        patch.name = "Fake.java"
        patch.parse("@@ -1,3 +1,1 @@ public class Main{\n+     if ((e.getChangeFlags() & e.PARENT_CHANGED) > 0);\n}")
        detector = ChekBitSigned()
        detector.visit([patch])
        detector.report()
        assert len(detector.bug_accumulator) == 1