import pytest

from patterns.models.context import Context
from rparser import parse
from patterns.models.engine import DefaultEngine

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
]


@pytest.mark.parametrize('pattern_type,file_name,patch_str,expected_length,line_no', params)
def test(pattern_type: str, file_name: str, patch_str: str, expected_length: int, line_no: int):
    patch = parse(patch_str, False)
    patch.name = file_name
    engine = DefaultEngine(Context(), included_filter=('UselessSubstringDetector',))
    engine.visit(patch)
    if expected_length > 0:
        assert len(engine.bug_accumulator) == expected_length
        assert engine.bug_accumulator[0].line_no == line_no
        assert engine.bug_accumulator[0].type == pattern_type
    else:
        assert len(engine.bug_accumulator) == 0
