from rparser import Patch
from patterns.detect.fi_public_should_be_protected import FiPublicShouldBeProtected

class TestFiPublicShouldBeProtected:

    # From other repository: https: // github.com / ustcweizhou / libvirt - java / commit / c827e87d958d1cb7a969747fcb6c8c1724a7889d
    def test_Fi_Public_Should_Be_Protected_01(self):
        patch = Patch()
        patch.name = "Connect.java"
        patch.parse(
            "@@ -533,6 +533,7 @@ public String domainXMLToNative(String nativeFormat, String domainXML, int flags\n     }\n \n     @Override\n+    public void finalize() throws LibvirtException {\n       close();\n     }\n ")
        detector = FiPublicShouldBeProtected()
        detector.visit([patch])
        assert len(detector.bug_accumulator) == 1
