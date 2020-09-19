from rparser import Patch
from patterns.detect.empty_zip_file_entry import EmptyZipFileEntry


class TestAmCreatesEmptyZipFileEntry:

    #From spotBugs:https://github.com/spotbugs/spotbugs/blob/3883a7b750fb339577be073bc45e36b6f268777b/spotbugsTestCases/src/java/bugPatterns/AM_CREATES_EMPTY_ZIP_FILE_ENTRY.java
    def test_AM_CREATES_EMPTY_ZIP_FILE_ENTRY_01(self):
        patch = Patch()
        patch.name = "xxxx.java"
        patch.parse("@@ -622,5 +622,4 @@      void bug(ZipOutputStream any, ZipEntry anyZipEntry) throws IOException {\n"
                    "           out.putNextEntry(feedbackSubAttachmentFolderEntry);\n"
                    "-           out.flush();\n"
                    "           out.closeEntry(); \n }")
        detector = EmptyZipFileEntry()
        detector.visit([patch])
        assert len(detector.bug_accumulator) == 1
        bugins = detector.bug_accumulator[0]
        assert bugins.type == 'AM_CREATES_EMPTY_ZIP_FILE_ENTRY'
        assert bugins.line_no == 623


    #DIY
    def test_AM_CREATES_EMPTY_ZIP_FILE_ENTRY_02(self):
        patch = Patch()
        patch.name = "xxxx.java"
        patch.parse("@@ -62,6 +62,5 @@      void bug(ZipOutputStream any, ZipEntry anyZipEntry) throws IOException {\n"
                    "     out.putNextEntry(feedbackSubAttachmentFolderEntry);\n"
                    "\n"
                    "    out.closeEntry(); \n }")
        detector = EmptyZipFileEntry()
        detector.visit([patch])
        assert len(detector.bug_accumulator) == 1
        bugins = detector.bug_accumulator[0]
        assert bugins.type == 'AM_CREATES_EMPTY_ZIP_FILE_ENTRY'
        assert bugins.line_no == 64
