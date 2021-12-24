import pytest

from codegex.models.context import Context
from codegex.utils.rparser import parse
from codegex.models.engine import DefaultEngine

params = [
    # --------------- IIO_INEFFICIENT_INDEX_OF ---------------
    # From SpotBugs: https://github.com/spotbugs/spotbugs/blob/51e586bed98393e53559a38c1f9bd15f54514efa/spotbugsTestCases/src/java/DumbMethodInvocations.java
    ('IIO_INEFFICIENT_INDEX_OF', 'TestUselessSubstringDetector_01.java',
     '''@ExpectWarning("IIO_INEFFICIENT_INDEX_OF")
    int notBug2(String any) {
        return any.indexOf(".");
    }
    ''', 1, 3),
    ('IIO_INEFFICIENT_INDEX_OF', 'TestUselessSubstringDetector_01.java',
     '''@NoWarning("RE_POSSIBLE_UNINTENDED_PATTERN")
    @ExpectWarning("IIO_INEFFICIENT_INDEX_OF")
    int notBug22(String any) {
        return any.indexOf("|");
    }
    ''', 1, 4),
    # From Github: https://github.com/openjdk/jfx17u/commit/8488a6fd03cc514dfb6214ffa62f2ab533e7baf4
    ('IIO_INEFFICIENT_INDEX_OF', 'TestInefficientIndexOfDetector_02.java',
     '''if (fieldSig.indexOf(".") >= 0)''', 1, 1),
    # --------------- IIO_INEFFICIENT_LAST_INDEX_OF ---------------
    ('IIO_INEFFICIENT_LAST_INDEX_OF', 'TestInefficientIndexOfDetector_02.java',
     '''int i = className.lastIndexOf("$");''', 1, 1),
    # From Github: https://github.com/lgtminshi/self_spotbugs/commit/4210c99bd9394bd804f8252794a8542a3919ef4b
    ('IIO_INEFFICIENT_LAST_INDEX_OF', 'TestInefficientIndexOfDetector_02.java',
     '''if (one.contains("$") && two.contains("$")
                        && one.substring(0, one.lastIndexOf("$")).equals(two.substring(0, two.lastIndexOf("$"))))
    ''', 1, 2),

    # From Github: https://github.com/Sandec/jfx/commit/8488a6fd03cc514dfb6214ffa62f2ab533e7baf4
    ('IIO_INEFFICIENT_INDEX_OF', 'TestInefficientIndexOfDetector_02.java',
     '''packageLine.append(controller.substring(0, controller.indexOf(".")));''', 1, 1),

    # From Github: https://github.com/Sandec/jfx/commit/8488a6fd03cc514dfb6214ffa62f2ab533e7baf4
    ('IIO_INEFFICIENT_INDEX_OF', 'TestInefficientIndexOfDetector_02.java',
     '''int dotIndex = style.indexOf(":");''', 1, 1),
    # DIY
    ('IIO_INEFFICIENT_INDEX_OF', 'TestInefficientIndexOfDetector_03.java',
     '''int dotIndex = style
                            .indexOf(":");''', 1, 2),

]


@pytest.mark.parametrize('pattern_type,file_name,patch_str,expected_length,line_no', params)
def test(pattern_type: str, file_name: str, patch_str: str, expected_length: int, line_no: int):
    patch = parse(patch_str, False)
    patch.name = file_name
    engine = DefaultEngine(Context(), included_filter=('InefficientIndexOfDetector',))
    engine.visit(patch)
    if expected_length > 0:
        assert len(engine.bug_accumulator) == expected_length
        assert engine.bug_accumulator[0].line_no == line_no
        assert engine.bug_accumulator[0].type == pattern_type
    else:
        assert len(engine.bug_accumulator) == 0
