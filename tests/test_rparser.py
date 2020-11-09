import pytest

from patterns.detect.find_finalize_invocations import FindFinalizeInvocations
from rparser import parse

params = [(True, FindFinalizeInvocations(), 'FI_EXPLICIT_INVOCATION', 'Fake.java',
             '''@@ -1 +1,21 @@
             void bug(FI_EXPLICIT_INVOCATION any) throws Throwable {
                 any.finalize();
             }''', 1, 2),
          (False, FindFinalizeInvocations(), 'FI_EXPLICIT_INVOCATION', 'Fake.java',
               '''void bug(FI_EXPLICIT_INVOCATION any) throws Throwable {
                   any.finalize();
               }''', 1, 2)
          ]

@pytest.mark.parametrize('is_patch,detector,pattern_type,file_name,patch_str,expected_length,line_no', params)
def test(is_patch:bool, detector, pattern_type: str, file_name: str, patch_str: str, expected_length: int, line_no: int):
    patch = parse(patch_str, is_patch)
    patch.name = file_name
    detector.visit([patch])
    if expected_length > 0:
        assert len(detector.bug_accumulator) == expected_length
        assert detector.bug_accumulator[0].line_no == line_no
        assert detector.bug_accumulator[0].type == pattern_type
    else:
        assert len(detector.bug_accumulator) == 0