import pytest

from patterns.models.context import Context
from rparser import parse
from patterns.models.engine import DefaultEngine

params = [
    # --------------- RV_DONT_JUST_NULL_CHECK_READLINE ---------------
    # From Github: https://github.com/icyphy/ptII/commit/24a492a88c7d989b4503e8023a739363ad98c7ac
    ('RV_DONT_JUST_NULL_CHECK_READLINE', 'TestDontJustCheckReadline_01.java',
     '''while (input.readLine() != null) {
                    count++;}
    ''', 1, 1),

]


@pytest.mark.parametrize('pattern_type,file_name,patch_str,expected_length,line_no', params)
def test(pattern_type: str, file_name: str, patch_str: str, expected_length: int, line_no: int):
    patch = parse(patch_str, False)
    patch.name = file_name
    engine = DefaultEngine(Context(), included_filter=('DontJustCheckReadlineDetector',))
    engine.visit(patch)
    if expected_length > 0:
        assert len(engine.bug_accumulator) == expected_length
        assert engine.bug_accumulator[0].line_no == line_no
        assert engine.bug_accumulator[0].type == pattern_type
    else:
        assert len(engine.bug_accumulator) == 0