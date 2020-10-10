import pytest

from patterns.detect.infinite_recursive_loop import InfiniteRecursiveLoop
from rparser import Patch

params = [
    #  From other repository: https://github.com/vavr-io/vavr/pull/1752#discussion_r92956593
    ('IL_CONTAINER_ADDED_TO_ITSELF', 'Fake.java',
    '''@@ -14,8 +15,9 @@
    final java.util.List<Object> testee = empty();
    testee.add(testee);
    assertThat(testee.containsAll(testee)).isTrue();
    ''', 1, 16)
]

@pytest.mark.parametrize('pattern_type,file_name,patch_str,expected_length,line_no', params)
def test(pattern_type: str, file_name: str, patch_str: str, expected_length: int, line_no: int):
    patch = Patch()
    patch.name = file_name
    patch.parse(patch_str)
    detector = InfiniteRecursiveLoop()
    detector.visit([patch])
    if expected_length > 0:
        assert len(detector.bug_accumulator) == expected_length
        assert detector.bug_accumulator[0].line_no == line_no
        assert detector.bug_accumulator[0].type == pattern_type
    else:
        assert len(detector.bug_accumulator) == 0