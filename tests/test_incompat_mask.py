import pytest

from patterns.detect.incompat_mask import *
from patterns.detectors import DefaultEngine
from rparser import parse

params = [
    # From other repository: https://github.com/albfan/jmeld/commit/bab5df4d96b511dd1e4be36fce3a2eab52c24c4e
    (True, 'BIT_SIGNED_CHECK', "Fake.java",
            "@@ -51,7 +51,7 @@ public void hierarchyChanged(HierarchyEvent e)\n         {\n           JRootPane "
            "rootPane;\n \n+          if ((e.getChangeFlags() & e.PARENT_CHANGED) > 0)\n+          if (("
            "e.getChangeFlags() & e.PARENT_CHANGED) != 0)\n           {\n             rootPane = getRootPane();\n     "
            "        if (rootPane == null)}", 1, 54),
    # From other repository: https://github.com/bndtools/bnd/commit/68c73f78ef7de5234714b350a7d0b8760f9eaf1a
    (True, 'BIT_SIGNED_CHECK', "Fake.java",
            "@@ -222,7 +222,7 @@ public void resourceChanged(IResourceChangeEvent event) {\n         if (delta == "
            "null)\n             return;\n \n+        if ((delta.getKind() & IResourceDelta.CHANGED) > 0 && ("
            "delta.getFlags() & IResourceDelta.MARKERS) > 0) {\n+        if ((delta.getKind() & "
            "IResourceDelta.CHANGED) != 0 && (delta.getFlags() & IResourceDelta.MARKERS) != 0) {\n             "
            "getEditorSite().getShell().getDisplay().asyncExec(new Runnable() {\n                 public void run() {"
            "\n                     loadProblems();", 1, 225),

    # DIY
    (True, 'BIT_SIGNED_CHECK', "Fake.java",
            "@@ -3,6 +3,8 @@  public static void main(String[] args){\n        int a = 1; int b = -1;\n+        "
            "Boolean test_var1 = (a&b)>0;\n        int     test_var2 = -1;\n +        if(test_var1&& test_var2 >0){\n "
            "           System.out.println(\"branch1\");\n        }\n    }  ", 1, 4),

    # DIY   two errors in different lines
    (True, 'BIT_SIGNED_CHECK', "Fake.java",
            "@@ -51,7 +51,7 @@ public void hierarchyChanged(HierarchyEvent e)\n         {\n           JRootPane "
            "rootPane;\n \n+          if ((e.getChangeFlags() & e.PARENT_CHANGED) > 0)\n"
            "{\n             rootPane = getRootPane();\n             if ("
            "rootPane == null)}", 1, 54),

    # DIY   two errors in one line
    (True, 'BIT_SIGNED_CHECK', "Fake.java",
            "@@ -51,7 +51,7 @@ public void hierarchyChanged(HierarchyEvent e)\n         {\n           JRootPane "
            "rootPane;\n \n+          if ((e.getChangeFlags() & 0) == 0 &&(e.getChangeFlags() & e.PARENT_CHANGED)> 0)\n              {\n             rootPane = getRootPane("
            ");\n             if (rootPane == null)}", 2, 54),
    ]


@pytest.mark.parametrize('is_patch,pattern_type,file_name,patch_str,expected_length,line_no', params)
def test(is_patch: bool, pattern_type: str, file_name: str, patch_str: str, expected_length: int,
         line_no: int):
    patch = parse(patch_str, is_patch)
    patch.name = file_name
    engine = DefaultEngine([BitSignedCheck(), BitSignedCheckAndBitAndZZDetector()])
    engine.visit([patch])
    if expected_length > 0:
        assert len(engine.bug_accumulator) == expected_length
        assert engine.bug_accumulator[0].line_no == line_no
        assert engine.bug_accumulator[0].type == pattern_type
    else:
        assert len(engine.bug_accumulator) == 0
