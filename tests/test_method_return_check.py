from patterns.detect.method_return_check import MethodReturnCheck
from rparser import Patch


class TestMethodReturnCheck:
    # https://github.com/spotbugs/spotbugs/blob/3883a7b750fb339577be073bc45e36b6f268777b/spotbugsTestCases/src/java/bugIdeas/Ideas_2011_11_02.java
    def test_RV_EXCEPTION_NOT_THROWN_01(self):
        patch = Patch()
        patch.name = "Ideas_2011_11_02.java"
        patch.parse('''@@ -11,3 +11,3 @@ public class Ideas_2011_11_02 {
            public void setCheckedElements(Object[] elements) {
                 new UnsupportedOperationException();
        }''')
        detector = MethodReturnCheck()
        detector.visit([patch])
        detector.report()
        assert len(detector.bug_accumulator) == 1
        assert detector.bug_accumulator[0].line_no == 12

    # https://github.com/bndtools/bnd/commit/960664b12a8f8886779617a283883cdc901cef5e
    def test_RV_EXCEPTION_NOT_THROWN_02(self):
        patch = Patch()
        patch.name = "Clazz.java"
        patch.parse('''@@ -1114,6 +1114,7 @@ void doSignature(DataInputStream in, ElementType member, int access_flags) throw
				classSignature = signature;

		} catch (Exception e) {
+	        new RuntimeException("Signature failed for" + signature, e);
		}
	}

        ''')
        detector = MethodReturnCheck()
        detector.visit([patch])
        detector.report()
        assert len(detector.bug_accumulator) == 1
        assert detector.bug_accumulator[0].line_no == 1117
