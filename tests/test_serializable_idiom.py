import pytest

from patterns.detect.serializable_idiom import SerializableIdiom
from rparser import Patch


params = [
    # https://github.com/mhagnumdw/bean-info-generator/pull/5/files#diff-71bf0b35fa483782180f548a1a7d6cc4b3822ed12aa4bb86640f80dde9df3077R13
    (SerializableIdiom(), 'SE_NONLONG_SERIALVERSIONID', 'Fake.java',
     '''@@ -0,0 +1,1 @@
     public static final BeanMetaInfo serialVersionUID = new BeanMetaInfo("serialVersionUID");''', 0, 1),
    (SerializableIdiom(), 'SE_NONLONG_SERIALVERSIONID', 'Fake.java',
     '''@@ -1,3 +1,1 @@ public class Main{\n+    static final int serialVersionUID = 10000;\n}''', 1, 1),

    # # https://github.com/EriolEandur/Animations/pull/2/files#diff-142800dac9917f3c0745c03ab73c4d007f454a841d1d17fa32294da970897172R230
    (SerializableIdiom(), 'SE_NONSTATIC_SERIALVERSIONID', 'Fake.java',
     '''@@ -0,0 +1,1 @@public static long getSerialVersionUID() {
        return serialVersionUID;
    }''', 0, 1),
    (SerializableIdiom(), 'SE_NONSTATIC_SERIALVERSIONID', 'Fake.java',
     '''@@ -1,3 +1,1 @@ public class Main{\n+    final long serialVersionUID = 10000L;''', 1, 1),

    (SerializableIdiom(), 'SE_NONFINAL_SERIALVERSIONID', 'Fake.java',
     '''@@ -1,3 +1,1 @@ public class Main{\n+    static long serialVersionUID = 10000L;\n}''', 1, 1)
]


@pytest.mark.parametrize('detector,pattern_type,file_name,patch_str,expected_length,line_no', params)
def test(detector, pattern_type: str, file_name: str, patch_str: str, expected_length: int, line_no: int):
    patch = Patch()
    patch.name = file_name
    patch.parse(patch_str)
    detector.visit([patch])
    if expected_length > 0:
        assert len(detector.bug_accumulator) == expected_length
        assert detector.bug_accumulator[0].line_no == line_no
        assert detector.bug_accumulator[0].type == pattern_type
    else:
        assert len(detector.bug_accumulator) == 0
