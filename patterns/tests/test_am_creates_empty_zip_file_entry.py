from rparser import Patch
from patterns.detect.am_creates_empty_zip_file_entry import AMCREATESEMPTYZIPFILEENTRY


class TestAMCREATESEMPTYZIPFILEENTRY:
    def test_01(self):
        patch = Patch()
        patch.name = "xxxx.java"
        patch.parse("@@ -622,5 +622,4 @@ ZipEntry feedbackSubAttachmentFolderEntry = new ZipEntry(  \n         feedbackSubAttachmentFolder);\n           out.putNextEntry(feedbackSubAttachmentFolderEntry);\n-    out.flush();\n        out.closeEntry();")
        detector = AMCREATESEMPTYZIPFILEENTRY()
        detector.visit([patch])
        assert len(detector.bug_accumulator) == 1
        detector.report()