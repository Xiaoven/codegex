import pytest

from patterns.models.engine import DefaultEngine
from rparser import parse
from patterns.models.priorities import *

params = [
    # https://github.com/spotbugs/spotbugs/blob/a6f9acb2932b54f5b70ea8bc206afb552321a222/spotbugsTestCases/src/java/bugPatterns/RE_POSSIBLE_UNINTENDED_PATTERN.java
    (False, 'RE_POSSIBLE_UNINTENDED_PATTERN', 'RE_POSSIBLE_UNINTENDED_PATTERN_01.java',
     '''@ExpectWarning("RE_POSSIBLE_UNINTENDED_PATTERN")
        String [] bug1(String any) {
            return any.split(".");
        }''', 1, 3, HIGH_PRIORITY),
    (False, 'RE_POSSIBLE_UNINTENDED_PATTERN', 'RE_POSSIBLE_UNINTENDED_PATTERN_02.java',
     '''String bug2(String any, String any2) {
            return any.replaceAll(".", any2);
        }''', 1, 2, MEDIUM_PRIORITY),
    (False, 'RE_POSSIBLE_UNINTENDED_PATTERN', 'RE_POSSIBLE_UNINTENDED_PATTERN_03.java',
     '''return any.replaceFirst(".", any2);''', 1, 1, HIGH_PRIORITY),
    (False, 'RE_POSSIBLE_UNINTENDED_PATTERN', 'RE_POSSIBLE_UNINTENDED_PATTERN_04.java',
     '''return any.split("|");''', 1, 1, HIGH_PRIORITY),
    (False, 'RE_POSSIBLE_UNINTENDED_PATTERN', 'RE_POSSIBLE_UNINTENDED_PATTERN_05.java',
     '''return any.replaceAll("|", any2);''', 1, 1, HIGH_PRIORITY),
    (False, 'RE_POSSIBLE_UNINTENDED_PATTERN', 'RE_POSSIBLE_UNINTENDED_PATTERN_06.java',
     '''return any.replaceFirst("|", any2);''', 1, 1, HIGH_PRIORITY),
    (False, 'RE_POSSIBLE_UNINTENDED_PATTERN', 'RE_POSSIBLE_UNINTENDED_PATTERN_07.java',
     '''return any.replaceAll("|", "*");''', 1, 1, HIGH_PRIORITY),
    (False, 'RE_POSSIBLE_UNINTENDED_PATTERN', 'RE_POSSIBLE_UNINTENDED_PATTERN_08.java',
     '''return any.replaceAll(".", "*");''', 0, 1, None),
    (False, 'RE_POSSIBLE_UNINTENDED_PATTERN', 'RE_POSSIBLE_UNINTENDED_PATTERN_09.java',
     '''return any.indexOf(".");''', 0, 1, None),
    (False, 'RE_POSSIBLE_UNINTENDED_PATTERN', 'RE_POSSIBLE_UNINTENDED_PATTERN_10.java',
     '''return any.indexOf("|");''', 0, 1, None),
    # DIY
    (False, 'RE_POSSIBLE_UNINTENDED_PATTERN', 'DIY_01.java',
     '''return any.matches("|");''', 1, 1, HIGH_PRIORITY),
    (False, 'RE_POSSIBLE_UNINTENDED_PATTERN', 'DIY_02.java',
     '''return customized.replaceAll("|", any2, arg3);''', 0, 1, None),
]


@pytest.mark.parametrize('is_patch,pattern_type,file_name,patch_str,expected_length,line_no,expected_priority', params)
def test(is_patch: bool, pattern_type: str, file_name: str, patch_str: str, expected_length: int,
         line_no: int, expected_priority: int):
    patch = parse(patch_str, is_patch)
    patch.name = file_name
    engine = DefaultEngine(included_filter=('SingleDotPatternDetector',))
    engine.visit(patch)
    if expected_length > 0:
        assert len(engine.bug_accumulator) == expected_length
        assert engine.bug_accumulator[0].line_no == line_no
        assert engine.bug_accumulator[0].type == pattern_type
        if expected_priority is not None:
            assert engine.bug_accumulator[0].priority == expected_priority
    else:
        assert len(engine.bug_accumulator) == 0