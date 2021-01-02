import pytest

from patterns.detect.method_return_check import NotThrowDetector
from patterns.models.engine import DefaultEngine
from rparser import parse

params = [
    # https://github.com/spotbugs/spotbugs/blob/3883a7b750fb339577be073bc45e36b6f268777b/spotbugsTestCases/src/java/bugIdeas/Ideas_2011_11_02.java
    ('RV_EXCEPTION_NOT_THROWN', 'Ideas_2011_11_02.java',
     '''@@ -11,3 +11,3 @@ public class Ideas_2011_11_02 {
            public void setCheckedElements(Object[] elements) {
                 new UnsupportedOperationException();
        }''', 1, 12),
    # https://github.com/bndtools/bnd/commit/960664b12a8f8886779617a283883cdc901cef5e
    ('RV_EXCEPTION_NOT_THROWN', 'Clazz.java',
     '''@@ -1114,6 +1114,7 @@ void doSignature(DataInputStream in, ElementType member, int access_flags) throw
				classSignature = signature;

		} catch (Exception e) {
+	        new RuntimeException("Signature failed for" + signature, e);
		}
	}''', 1, 1117),
]


@pytest.mark.parametrize('pattern_type,file_name,patch_str,expected_length,line_no', params)
def test(pattern_type: str, file_name: str, patch_str: str, expected_length: int, line_no: int):
    patch = parse(patch_str)
    patch.name = file_name
    engine = DefaultEngine(included_filter=['NotThrowDetector'])
    engine.visit([patch])
    if expected_length > 0:
        assert len(engine.bug_accumulator) == expected_length
        assert engine.bug_accumulator[0].line_no == line_no
        assert engine.bug_accumulator[0].type == pattern_type
    else:
        assert len(engine.bug_accumulator) == 0
