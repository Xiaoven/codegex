from rparser import Patch
from patterns.detect.am_creates_empty_zip_file_entry import AmCreatesEmptyZipFileEntry


class TestAmCreatesEmptyZipFileEntry:

    #From spotBugs:https://github.com/spotbugs/spotbugs/blob/3883a7b750fb339577be073bc45e36b6f268777b/spotbugsTestCases/src/java/bugPatterns/AM_CREATES_EMPTY_ZIP_FILE_ENTRY.java
    def test_AM_CREATES_EMPTY_ZIP_FILE_ENTRY_01(self):
        patch = Patch()
        patch.name = "xxxx.java"
        patch.parse("@@ -622,5 +622,4 @@      void bug(ZipOutputStream any, ZipEntry anyZipEntry) throws IOException {\n           out.putNextEntry(feedbackSubAttachmentFolderEntry);\n-    out.flush();\n        out.closeEntry(); \n }")
        detector = AmCreatesEmptyZipFileEntry()
        detector.visit([patch])
        assert len(detector.bug_accumulator) == 1

    #DIY
    def test_AM_CREATES_EMPTY_ZIP_FILE_ENTRY_02(self):
        patch = Patch()
        patch.name = "xxxx.java"
        patch.parse("@@ -62,6 +62,5 @@      void bug(ZipOutputStream any, ZipEntry anyZipEntry) throws IOException {\n           out.putNextEntry(feedbackSubAttachmentFolderEntry);\n-    out.flush();\n    \n    out.closeEntry(); \n }")
        detector = AmCreatesEmptyZipFileEntry()
        detector.visit([patch])
        assert len(detector.bug_accumulator) == 1
