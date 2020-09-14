from patterns.detect.incompat_mask import ChekBitSigned
from rparser import Patch

class TestChekSignOfBitoperation:

    # From other repository: https://github.com/albfan/jmeld/commit/bab5df4d96b511dd1e4be36fce3a2eab52c24c4e
    def test_INCOMPAT_MASK_BIT_SIGNED_CHECK_01(self):
        patch = Patch()
        patch.name = "Fake.java"
        patch.parse("@@ -51,7 +51,7 @@ public void hierarchyChanged(HierarchyEvent e)\n         {\n           JRootPane rootPane;\n \n+          if ((e.getChangeFlags() & e.PARENT_CHANGED) > 0)\n+          if ((e.getChangeFlags() & e.PARENT_CHANGED) != 0)\n           {\n             rootPane = getRootPane();\n             if (rootPane == null)}")
        detector = ChekBitSigned()
        detector.visit([patch])
        detector.report()
        assert len(detector.bug_accumulator) == 1
    # From other repository: https://github.com/bndtools/bnd/commit/68c73f78ef7de5234714b350a7d0b8760f9eaf1a
    def test_INCOMPAT_MASK_BIT_SIGNED_CHECK_02(self):
        patch = Patch()
        patch.name = "Fake.java"
        patch.parse("@@ -222,7 +222,7 @@ public void resourceChanged(IResourceChangeEvent event) {\n         if (delta == null)\n             return;\n \n+        if ((delta.getKind() & IResourceDelta.CHANGED) > 0 && (delta.getFlags() & IResourceDelta.MARKERS) > 0) {\n+        if ((delta.getKind() & IResourceDelta.CHANGED) != 0 && (delta.getFlags() & IResourceDelta.MARKERS) != 0) {\n             getEditorSite().getShell().getDisplay().asyncExec(new Runnable() {\n                 public void run() {\n                     loadProblems();")
        detector = ChekBitSigned()
        detector.visit([patch])
        detector.report()
        assert len(detector.bug_accumulator) == 1
    # DIY
    def test_INCOMPAT_MASK_BIT_SIGNED_CHECK_02(self):
        patch = Patch()
        patch.name = "Fake.java"
        patch.parse("@@ -3,6 +3,8 @@  public static void main(String[] args){\n        int a = 1; int b = -1;\n+        Boolean test_var1 = (a&b)>0;\n        int     test_var2 = -1;\n +        if(test_var1&& test_var2 >0){\n            System.out.println(\"branch1\");\n        }\n    }  ")
        detector = ChekBitSigned()
        detector.visit([patch])
        detector.report()
        assert len(detector.bug_accumulator) == 1