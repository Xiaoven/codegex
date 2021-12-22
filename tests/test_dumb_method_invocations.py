import pytest

from models.context import Context
from utils.rparser import parse
from models.engine import DefaultEngine

params = [
    # From SpotBugs: https://github.com/spotbugs/spotbugs/blob/51e586bed98393e53559a38c1f9bd15f54514efa/spotbugsTestCases/src/java/DumbMethodInvocations.java
    ('DMI_USELESS_SUBSTRING', 'TestUselessSubstringDetector_01.java',
     '''
     String f(String s) {return s.substring(0);}
    ''', 1, 2),
    # DIY
    ('DMI_USELESS_SUBSTRING', 'TestUselessSubstringDetector_02.java',
     '''
     String f(String msg) {return msg . substring ( 0 ) ;}
    ''', 1, 2),
    # ---------- DMI_HARDCODED_ABSOLUTE_FILENAME ---------- #
    # From SpotBugs:
    ('DMI_HARDCODED_ABSOLUTE_FILENAME', 'TestIsAbsoluteFileNameDetector_01.java',
     ''''@ExpectWarning("DMI_HARDCODED_ABSOLUTE_FILENAME")
    public void testFile() {
        new File("c:\\test.txt");
    }''', 1, 3),
    ('DMI_HARDCODED_ABSOLUTE_FILENAME', 'TestIsAbsoluteFileNameDetector_02.java',
     '''@ExpectWarning("DMI_HARDCODED_ABSOLUTE_FILENAME")
    public void testFile2() {
        new File("c:\\temp", "test.txt");
    }''', 1, 3),
    ('DMI_HARDCODED_ABSOLUTE_FILENAME', 'TestIsAbsoluteFileNameDetector_03.java',
     '''@ExpectWarning("DMI_HARDCODED_ABSOLUTE_FILENAME")
    public void testPrintStream() throws IOException {
        new PrintStream("c:\\test.txt", "UTF-8");
    }''', 1, 3),
    ('DMI_HARDCODED_ABSOLUTE_FILENAME', 'TestIsAbsoluteFileNameDetector_04.java',
     '''@NoWarning("DMI_HARDCODED_ABSOLUTE_FILENAME")
    public void testPrintStream2() throws IOException {
        new PrintStream("UTF-8", "c:\\test.txt");
    }''', 1, 3),
    # DIY
    ('DMI_HARDCODED_ABSOLUTE_FILENAME', 'TestIsAbsoluteFileNameDetector_05.java',
     'new PrintStream("/Users/codegex/Documents/projects", "UTF-8");', 1, 1),
    ('DMI_HARDCODED_ABSOLUTE_FILENAME', 'TestIsAbsoluteFileNameDetector_06.java',
     'new PrintStream("UTF-8", "/etc/aliases");', 0, 0),
    ('DMI_HARDCODED_ABSOLUTE_FILENAME', 'TestIsAbsoluteFileNameDetector_06.java',
     '"new PrintStream("UTF-8", \"/etc/aliases\");"', 0, 0),
]


@pytest.mark.parametrize('pattern_type,file_name,patch_str,expected_length,line_no', params)
def test(pattern_type: str, file_name: str, patch_str: str, expected_length: int, line_no: int):
    patch = parse(patch_str, False)
    patch.name = file_name
    engine = DefaultEngine(Context(), included_filter=('UselessSubstringDetector', 'IsAbsoluteFileNameDetector'))
    engine.visit(patch)
    if expected_length > 0:
        assert len(engine.bug_accumulator) == expected_length
        assert engine.bug_accumulator[0].line_no == line_no
        assert engine.bug_accumulator[0].type == pattern_type
    else:
        assert len(engine.bug_accumulator) == 0
