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
        bug_ins = detector.bug_accumulator[0]
        assert bug_ins.type == 'FI_EXPLICIT_INVOCATION'
        assert bug_ins.line_no == 622

    # From other repository: https: // github.com / ustcweizhou / libvirt - java / commit / c827e87d958d1cb7a969747fcb6c8c1724a7889d
    def test_FI_PUBLIC_SHOULD_BE_PROTECTED_01(self):
        patch = Patch()
        patch.name = "Connect.java"
        patch.parse(
            '''@@ -533,6 +533,7 @@ public String domainXMLToNative(String nativeFormat, String domainXML, int flags
                        }
                  
                        @Override
                   +    public void finalize() throws LibvirtException {
                          close();
                               }''')
        detector = FindFinalizeInvocations()
        detector.visit([patch])
        assert len(detector.bug_accumulator) == 1
        bug_ins = detector.bug_accumulator[0]
        assert bug_ins.type == 'FI_PUBLIC_SHOULD_BE_PROTECTED'
        assert bug_ins.line_no == 536


