import pytest

from codegex.models.context import Context
from codegex.models.engine import DefaultEngine
from codegex.utils.rparser import parse

params = [
    # https://github.com/spotbugs/spotbugs/blob/a6f9acb2932b54f5b70ea8bc206afb552321a222/spotbugsTestCases/src/java/bugPatterns/DMI_BAD_MONTH.java
    ('DMI_BAD_MONTH', 'DMI_BAD_MONTH.java',
     '''@ExpectWarning("DMI_BAD_MONTH")
        void bug(Date date) {
            date.setMonth(12);
        }''', 1, 3),
    # DIY
    ('DMI_BAD_MONTH', 'Fake_01.java',
     '''MyCalendar.set(Calendar.YEAR, 2020);
        MyCalendar.set(Calendar.MONTH, 12);''', 1, 2),
    ('DMI_BAD_MONTH', 'Fake_02.java',
     '''calendarInstance.set(Calendar.YEAR, 2021);
        calendarInstance.set(Calendar.MONTH, Calendar.JANUARY);''', 0, 1),
    ('DMI_BAD_MONTH', 'Fake_03.java',
     '''calendar.set(2021, 12, 10, ''', 1, 1),
    ('DMI_BAD_MONTH', 'Fake_04.java',
     '''void config(Calendar cal){
            cal.set(2021, 12, 10);''', 0, 1),
    ('DMI_BAD_MONTH', 'Fake_05.java',
     '''Calendar c = new GregorianCalendar(2020, 12, 1);''', 1, 1),
    # --------------- BSHIFT_WRONG_ADD_PRIORITY -----------------
    # DIY
    ('BSHIFT_WRONG_ADD_PRIORITY', 'Fake_06.java',
     '''int main(int foo, int var){
          return rst = foo << 32 + var;
        }''', 0, 2),
    ('BSHIFT_WRONG_ADD_PRIORITY', 'Fake_07.java',
     '''return foo << 16 + bar;''', 1, 1),
    ('BSHIFT_WRONG_ADD_PRIORITY', 'Fake_08.java',
     '''return foo << 8 + var;''', 1, 1),
    ('BSHIFT_WRONG_ADD_PRIORITY', 'Fake_09.java',
     '''return foo << 8 - var;''', 1, 1),
    ('BSHIFT_WRONG_ADD_PRIORITY', 'Fake_10.java',
     '''int constant = 16;
        return foo << constant + var;''', 1, 2),
    ('BSHIFT_WRONG_ADD_PRIORITY', 'Fake_10.java',
     '''long main(long foo, long var){
          return foo << 8L + var;''', 1, 2),
    # ------------------------ DLS_OVERWRITTEN_INCREMENT ------------------------
    # https://spotbugs.readthedocs.io/en/stable/bugDescriptions.html
    ('DLS_OVERWRITTEN_INCREMENT', 'Main_01.java',
     '''public class DLS_OVERWRITTEN_INCREMENT {
    void test(){
        int a = 3;
        a = a --;
    }
}
     ''', 1, 4),
    # DIY
    ('DLS_OVERWRITTEN_INCREMENT', 'Main_02.java',
     '''public class DLS_OVERWRITTEN_INCREMENT {
    void test(){
        int a=5;
        a = a ++;
    }
}
     ''', 1, 4),
    ('DLS_OVERWRITTEN_INCREMENT', 'Main_03.java',
     '''public class DLS_OVERWRITTEN_INCREMENT {
    void test(){
        int a=5;
        a=1 - a++;
    }
}
     ''', 1, 4),
    ('DLS_OVERWRITTEN_INCREMENT', 'Main_04.java',
     '''public class DLS_OVERWRITTEN_INCREMENT {
    void test(){
        int a=5;
        a=a ++ + 5;
    }
}
     ''', 1, 4),
    ('DLS_OVERWRITTEN_INCREMENT', 'Main_05.java',
     '''public class DLS_OVERWRITTEN_INCREMENT {
    void test(){
        int a=5, b;
        a=b / a --;
    }
}
     ''', 1, 4),
    # fp: https://github.com/Xiaoven/rbugs/issues/132
    ('DLS_OVERWRITTEN_INCREMENT', 'Main_09.java',
     '''public class DLS_OVERWRITTEN_INCREMENT {
    void test(){
        card.order = order++;
    }
}
     ''', 0, 1),
    ('DLS_OVERWRITTEN_INCREMENT', 'Main_10.java',
     '''public class DLS_OVERWRITTEN_INCREMENT {
    void test(){
        int s = status++;
    }
}
     ''', 0, 1),
    ('DLS_OVERWRITTEN_INCREMENT', 'Main_11.java',
     '''public class DLS_OVERWRITTEN_INCREMENT {
    void test(){
        final int numFinished = ++verticesFinished;
        final int numFinished = ++numFinishedVertices;
    }
}
     ''', 0, 1),
    ('PZ_DONT_REUSE_ENTRY_OBJECTS_IN_ITERATORS', 'Main_12.java',
     "public class TMP implements Iterator, Map.Entry {", 1, 1),
    ('PZ_DONT_REUSE_ENTRY_OBJECTS_IN_ITERATORS', 'Main_13.java',
     "public interface TMP extends Iterator, Entry {", 1, 1),
    ('IM_MULTIPLYING_RESULT_OF_IREM', 'ReuseEntryInIteratorDetectorTest_01.java',
     "return i % 60 * 1000;", 1, 1),
    ('DMI_INVOKING_TOSTRING_ON_ANONYMOUS_ARRAY', 'AnonymousArrayToStringDetector_01.java',
     'System.out.println((new String[] { new String("one"), "two" }).toString());', 1, 1),
    # TODO: FN. The parser will split the following statement as several lines
    ('DMI_INVOKING_TOSTRING_ON_ANONYMOUS_ARRAY', 'AnonymousArrayToStringDetector_02.java',
     '''System.out.println((new Integer[] {
                1,
                2 } ).toString());''', 0, 1),
    # ------------------------ BX_BOXING_IMMEDIATELY_UNBOXED ------------------------
    # DIY
    ('BX_BOXING_IMMEDIATELY_UNBOXED', 'TestBoxingImmediatelyUnboxedDetector_01.java',
     'new Float( value ).floatValue();', 1, 1),
    # From Github: https://github.com/NetCal/DNC/commit/cf312e5786a48959962f3b8fa2a765bfa979b3fd
    ('BX_BOXING_IMMEDIATELY_UNBOXED', 'TestBoxingImmediatelyUnboxedDetector_02.java',
     'return new Double( value ).doubleValue();', 1, 1),
    # From Github: https://github.com/NetCal/DNC/commit/daa1044bf55794f28e750de15ae3fc4f6df0bb09
    ('BX_BOXING_IMMEDIATELY_UNBOXED', 'TestBoxingImmediatelyUnboxedDetector_03.java',
     'rfloat num_float = new Float( num.doubleValue() ).floatValue();', 1, 1),
    # ------------------------ BX_BOXING_IMMEDIATELY_UNBOXED_TO_PERFORM_COERCION ------------------------
    # From Github: https://github.com/ShoOgino/poiMethod202104/commit/4c2543c107bc1f63954d0d5d1d03c568793920e9
    ('BX_BOXING_IMMEDIATELY_UNBOXED_TO_PERFORM_COERCION', 'TestBoxingImmediatelyUnboxedDetector_04.java',
     'strb.append(new Double(realINum).intValue());', 1, 1),
    # From Github: https://github.com/halober/ovirt-engine/commit/533980c59d1cc8ba519eff67310a3eabb7dae508
    ('BX_BOXING_IMMEDIATELY_UNBOXED_TO_PERFORM_COERCION', 'TestBoxingImmediatelyUnboxedDetector_05.java',
     'formatTime.append((new Double(time/SECONDS_IN_A_DAY)).intValue());', 1, 1),
]


@pytest.mark.parametrize('pattern_type,file_name,patch_str,expected_length,line_no', params)
def test(pattern_type: str, file_name: str, patch_str: str, expected_length: int, line_no: int):
    patch = parse(patch_str, False)
    patch.name = file_name
    engine = DefaultEngine(Context(), included_filter=(
        'BadMonthDetector', 'ShiftAddPriorityDetector', 'OverwrittenIncrementDetector', 'ReuseEntryInIteratorDetector',
        'MultiplyIRemResultDetector', 'AnonymousArrayToStringDetector', 'BoxingImmediatelyUnboxedDetector',
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
