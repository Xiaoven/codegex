from rparser import Patch
from patterns.detect.fi_public_should_be_protected import FiPublicShouldBeProtected

class TestFiPublicShouldBeProtected:
    def test01(self):
        patch = Patch()
        patch.name = "Connect.java"
        patch.parse(
            "@@ -533,6 +533,7 @@ public String domainXMLToNative(String nativeFormat, String domainXML, int flags\n     }\n \n     @Override\n+    public void finalize() throws LibvirtException {\n       close();\n     }\n ")
        detector = FiPublicShouldBeProtected()
        detector.visit([patch])
        assert len(detector.bug_accumulator) == 1
        detector.report()
