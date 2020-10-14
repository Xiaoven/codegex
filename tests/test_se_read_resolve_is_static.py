import pytest
from patterns.detect.se_read_resolve_is_static import SeReadResolveIsStatic
from rparser import Patch
params = [
    #  From https://blog.csdn.net/zmx729618/article/details/52814472
    ('SE_READ_RESOLVE_IS_STATIC', 'xxx.java',
    '''@@ -0,0 +1,10 @@
    public final class MySingleton implements Serializable{
    private MySingleton() { }
    private static final MySingleton INSTANCE = new MySingleton();
    public static MySingleton getInstance() { return INSTANCE; }
    private static Object readResolve() throws ObjectStreamException {
    // instead of the object we're on,
    // return the class variable INSTANCE
    return INSTANCE;
    }
    }
    ''', 1, 5)
]

@pytest.mark.parametrize('pattern_type,file_name,patch_str,expected_length,line_no', params)
def test(pattern_type: str, file_name: str, patch_str: str, expected_length: int, line_no: int):
    patch = Patch()
    patch.name = file_name
    patch.parse(patch_str)
    detector = SeReadResolveIsStatic()
    detector.visit([patch])
    if expected_length > 0:
        assert len(detector.bug_accumulator) == expected_length
        assert detector.bug_accumulator[0].line_no == line_no
        assert detector.bug_accumulator[0].type == pattern_type
    else:
        assert len(detector.bug_accumulator) == 0