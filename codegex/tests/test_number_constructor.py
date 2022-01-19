from codegex.models.context import Context
from codegex.utils.rparser import parse
from codegex.models.engine import DefaultEngine

import pytest

params = [
    (False, 'DM_NUMBER_CTOR', 'TestNumberCTORDetector_01.java',
     """    public String test1(int myInt) {
        return new Integer(myInt).toString();
    }""", 1, 2),
    (False, 'DM_NUMBER_CTOR', 'TestNumberCTORDetector_02.java',
     'return new Integer("123");', 1, 1),
    (False, 'DM_NUMBER_CTOR', 'TestNumberCTORDetector_03.java',
     "escapeChars.put(new Character('n'), new Character('\n'));", 1, 1),
    (False, 'DM_NUMBER_CTOR', 'TestNumberCTORDetector_04.java',
     '''av.visit(name, new Character(
                    (char) readInt(items[readUnsignedShort(v)])));''', 1, 2),
    (False, 'DM_NUMBER_CTOR', 'TestNumberCTORDetector_05.java',
     '''seq.setBioBegin((seqDetails[1] == null || seqDetails[1].trim().equals("") ? null : new Integer(
    seqDetails[1])));''', 1, 2),
    (False, 'DM_FP_NUMBER_CTOR', 'TestFPNumberCTORDetector_01.java',
     'System.out.println(new Double(3.14));', 1, 1),
    (False, 'DM_FP_NUMBER_CTOR', 'TestFPNumberCTORDetector_02.java',
     'System.out.println(new Float("3.2f"));', 1, 1),
]


@pytest.mark.parametrize('is_patch,pattern_type,file_name,patch_str,expected_length,line_no', params)
def test(is_patch: bool, pattern_type: str, file_name: str, patch_str: str, expected_length: int, line_no: int):
    patch = parse(patch_str, is_patch)
    patch.name = file_name
    engine = DefaultEngine(Context(), included_filter=(
        'FPNumberCTORDetector', 'NumberCTORDetector'
    ))

    engine.visit(patch)
    find = False
    cnt = 0
    for instance in engine.bug_accumulator:
        if instance.type == pattern_type:
            cnt += 1
            if instance.line_no == line_no:
                find = True

    if expected_length > 0:
        assert find
        assert expected_length == cnt
    else:
        assert not find
