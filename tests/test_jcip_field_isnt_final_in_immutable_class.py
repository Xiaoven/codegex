import pytest
from patterns.detect.jcip_field_isnt_final_in_immutable_class import JcipFieldIsntFinalInImmutableClass
from rparser import Patch
params = [
    #  From https://wenwen.sogou.com/z/q912319033.htm
    ('JCIP_FIELD_ISNT_FINAL_IN_IMMUTABLE_CLASS', 'xxx.java',
    '''@@ -0,0 +1,3 @@
    public class String implements java.io.Serializable, Comparable<String>, CharSequence {
    private final char value[];
    }
    ''', 1, 1)
]

@pytest.mark.parametrize('pattern_type,file_name,patch_str,expected_length,line_no', params)
def test(pattern_type: str, file_name: str, patch_str: str, expected_length: int, line_no: int):
    patch = Patch()
    patch.name = file_name
    patch.parse(patch_str)
    detector = JcipFieldIsntFinalInImmutableClass()
    detector.visit([patch])
    if expected_length > 0:
        assert len(detector.bug_accumulator) == expected_length
        assert detector.bug_accumulator[0].line_no == line_no
        assert detector.bug_accumulator[0].type == pattern_type
    else:
        assert len(detector.bug_accumulator) == 0