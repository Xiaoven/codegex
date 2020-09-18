from patterns.detect.find_finalize_invocations import FindFinalizeInvocations
from rparser import Patch



class Test:
    # From spotBugs: https://github.com/spotbugs/spotbugs/blob/3883a7b750fb339577be073bc45e36b6f268777b/spotbugsTestCases/src/java/bugPatterns/FI_EXPLICIT_INVOCATION.java
    def test_FI_EXPLICIT_INVOCATION_01(self):
        patch = Patch()
        patch.name = "Fake.java"
        patch.parse('''@@ -622,7 +622,7 @@     void bug(FI_EXPLICIT_INVOCATION any) throws Throwable {
                    any.finalize();
                }''')
        detector = FindFinalizeInvocations()
        detector.visit([patch])
        assert len(detector.bug_accumulator) == 1


