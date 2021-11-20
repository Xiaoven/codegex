import pytest

from patterns.models.context import Context
from patterns.models.engine import DefaultEngine
from rparser import parse

params = [
    (False, 'NO_NOTIFY_NOT_NOTIFYALL', 'WaitInLoopTest_01.java',
     "obj.notify();", 1, 1),
]


@pytest.mark.parametrize('is_patch,pattern_type,file_name,patch_str,expected_length,line_no', params)
def test(is_patch: bool, pattern_type: str, file_name: str, patch_str: str, expected_length: int, line_no: int):
    patch = parse(patch_str, is_patch)
    patch.name = file_name

    engine = DefaultEngine(Context(), included_filter=['NotifyDetector'])
    engine.visit(patch)

    if expected_length > 0:
        assert len(engine.bug_accumulator) == expected_length
        assert engine.bug_accumulator[0].line_no == line_no
        assert engine.bug_accumulator[0].type == pattern_type
    else:
        assert len(engine.bug_accumulator) == 0
