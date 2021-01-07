import pytest

from patterns.models.engine import DefaultEngine
from rparser import parse

params = [
    # https://github.com/mhagnumdw/bean-info-generator/pull/5/files#diff-71bf0b35fa483782180f548a1a7d6cc4b3822ed12aa4bb86640f80dde9df3077R13
    (False, 'SA_SELF_COMPUTATION', 'Ideas_2013_11_06.java ',
     '''@NoWarning("SA_FIELD_SELF_COMPUTATION")
        public int testUpdate() {
            return flags ^(short) flags;
        }''', 0, 1),
    # https://github.com/spotbugs/spotbugs/blob/3883a7b750fb339577be073bc45e36b6f268777b/spotbugsTestCases/src/java/SelfFieldOperation.java#L25
    (False, 'SA_SELF_COMPUTATION', 'SelfFieldOperation.java',
     '''@ExpectWarning("SA_FIELD_SELF_COMPARISON,SA_FIELD_SELF_COMPUTATION")
        int f() {
            if (x < x)
                x = (int) ( y ^ y);
            if (x != x)
                y = x | x;
            if (x >= x)
                x = (int)(y & y);
            if (y > y)
                y = x - x;
            return x;
        }''', 4, 3),
]


@pytest.mark.parametrize('is_patch,pattern_type,file_name,patch_str,expected_length,line_no', params)
def test(is_patch: bool, pattern_type: str, file_name: str, patch_str: str, expected_length: int, line_no: int):
    patch = parse(patch_str, is_patch)
    engine = DefaultEngine(included_filter=['CheckForSelfOperation'])
    engine.visit(patch)
    if expected_length > 0:
        assert len(engine.bug_accumulator) == expected_length
        assert engine.bug_accumulator[0].line_no == line_no
        assert engine.bug_accumulator[0].type == pattern_type
    else:
        assert len(engine.bug_accumulator) == 0
