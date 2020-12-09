import pytest

from patterns.detect.serializable_idiom import DefSerialVersionID, DefReadResolveMethod
from patterns.detectors import DefaultEngine
from rparser import parse

params = [
    # https://github.com/mhagnumdw/bean-info-generator/pull/5/files#diff-71bf0b35fa483782180f548a1a7d6cc4b3822ed12aa4bb86640f80dde9df3077R13
    (True, 'SE_NONLONG_SERIALVERSIONID', 'Fake.java',
     '''@@ -0,0 +1,1 @@
     public static final BeanMetaInfo serialVersionUID = new BeanMetaInfo("serialVersionUID");''', 0, 1),
    (True, 'SE_NONLONG_SERIALVERSIONID', 'Fake.java',
     '''@@ -1,3 +1,1 @@ public class Main{\n+    static final int serialVersionUID = 10000;\n}''', 1, 1),

    # # https://github.com/EriolEandur/Animations/pull/2/files#diff-142800dac9917f3c0745c03ab73c4d007f454a841d1d17fa32294da970897172R230
    (True, 'SE_NONSTATIC_SERIALVERSIONID', 'Fake.java',
     '''@@ -0,0 +1,1 @@public static long getSerialVersionUID() {
        return serialVersionUID;
    }''', 0, 1),
    (True, 'SE_NONSTATIC_SERIALVERSIONID', 'Fake.java',
     '''@@ -1,3 +1,1 @@ public class Main{\n+    final long serialVersionUID = 10000L;''', 1, 1),

    (True, 'SE_NONFINAL_SERIALVERSIONID', 'Fake.java',
     '''@@ -1,3 +1,1 @@ public class Main{\n+    static long serialVersionUID = 10000L;\n}''', 1, 1),

    # ---------------- SE_READ_RESOLVE_MUST_RETURN_OBJECT DIY Tests -----------------
    (False, 'SE_READ_RESOLVE_MUST_RETURN_OBJECT', 'Fake.java',
     '''public class Main implements Serializable {
            static String readResolve() throws ObjectStreamException {
                return null;
            }
        }''', 1, 2),
    (False, 'SE_READ_RESOLVE_MUST_RETURN_OBJECT', 'Fake.java',
     '''public class Main implements Serializable {
            public Object readResolve() throws ObjectStreamException {
                return null;
            }
        }''', 0, 0),
    # ---------------- SE_READ_RESOLVE_IS_STATIC DIY Tests -----------------
    (False, 'SE_READ_RESOLVE_IS_STATIC', 'Fake.java',
     '''public class Main implements Serializable {
            private static Object readResolve() throws ObjectStreamException {
                return null;
            }
        }''', 1, 2),
    (False, 'SE_READ_RESOLVE_IS_STATIC', 'Fake.java',
     '''public class Main implements Serializable {
            public static final Object readResolve() throws ObjectStreamException {
                return null;
            }
        }''', 1, 2),
]


@pytest.mark.parametrize('is_patch,pattern_type,file_name,patch_str,expected_length,line_no', params)
def test(is_patch: bool, pattern_type: str, file_name: str, patch_str: str, expected_length: int, line_no: int):
    patch = parse(patch_str, is_patch)
    patch.name = file_name
    engine = DefaultEngine([DefSerialVersionID(), DefReadResolveMethod() ])
    engine.visit([patch])
    if expected_length > 0:
        assert len(engine.bug_accumulator) == expected_length
        assert engine.bug_accumulator[0].line_no == line_no
        assert engine.bug_accumulator[0].type == pattern_type
    else:
        assert len(engine.bug_accumulator) == 0