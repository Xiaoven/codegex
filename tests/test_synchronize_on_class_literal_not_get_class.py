import pytest

from patterns.models.context import Context
from patterns.models.engine import DefaultEngine
from rparser import parse

params = [
    (False, 'WL_USING_GETCLASS_RATHER_THAN_CLASS_LITERAL', 'SynGetClassTest_01.java',
     "synchronized( getClass ( ))\n    {", 1, 1),
    (False, 'WL_USING_GETCLASS_RATHER_THAN_CLASS_LITERAL', 'SynGetClassTest_02.java',
     " synchronized ( this.getClass() ) {\n", 1, 1),
]


@pytest.mark.parametrize('is_patch,pattern_type,file_name,patch_str,expected_length,line_no', params)
def test(is_patch: bool, pattern_type: str, file_name: str, patch_str: str, expected_length: int, line_no: int):
    patch = parse(patch_str, is_patch)
    patch.name = file_name

    engine = DefaultEngine(Context(), included_filter=['SynGetClassDetector'])
    engine.visit(patch)

    if expected_length > 0:
        assert len(engine.bug_accumulator) == expected_length
        assert engine.bug_accumulator[0].line_no == line_no
        assert engine.bug_accumulator[0].type == pattern_type
    else:
        assert len(engine.bug_accumulator) == 0
