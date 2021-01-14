import pytest

from patterns.models.engine import DefaultEngine
from rparser import parse

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
    # ------------------------ DLS_OVERWRITTEN_INCREMENT ------------------------
    # https://spotbugs.readthedocs.io/en/stable/bugDescriptions.html
    ('DLS_OVERWRITTEN_INCREMENT', 'Main_01.java',
     '''public class DLS_OVERWRITTEN_INCREMENT {
    void test(){
        int a=5;
        a = a++;
    }
}
     ''', 1, 4),
    # DIY
    ('DLS_OVERWRITTEN_INCREMENT', 'Main_02.java',
     '''public class DLS_OVERWRITTEN_INCREMENT {
    void test(){
        int a=5;
        a = ++a;
    }
}
     ''', 1, 4),
    ('DLS_OVERWRITTEN_INCREMENT', 'Main_03.java',
     '''public class DLS_OVERWRITTEN_INCREMENT {
    void test(){
        int a=5;
        a=2 + ++a;
    }
}
     ''', 1, 4),
    ('DLS_OVERWRITTEN_INCREMENT', 'Main_04.java',
     '''public class DLS_OVERWRITTEN_INCREMENT {
    void test(){
        int a=5;
        a=++a - ++a;
    }
}
     ''', 1, 4),
    ('DLS_OVERWRITTEN_INCREMENT', 'Main_05.java',
     '''public class DLS_OVERWRITTEN_INCREMENT {
    void test(){
        int a=5, b;
        a=++b * ++a;
    }
}
     ''', 1, 4),
    ('DLS_OVERWRITTEN_INCREMENT', 'Main_06.java',
     '''public class DLS_OVERWRITTEN_INCREMENT {
    void test(){
        int a=5;
        a= a / ++a;
    }
}
     ''', 1, 4),
        ('DLS_OVERWRITTEN_INCREMENT', 'Main_06.java',
     '''public class DLS_OVERWRITTEN_INCREMENT {
    void test(){
        int a=5;
        a= a / --a;
    }
}
     ''', 1, 4),
    ('DLS_OVERWRITTEN_INCREMENT', 'Main_05.java',
     '''public class DLS_OVERWRITTEN_INCREMENT {
    void test(){
        int a=5, b;
        a=++b * --a;
    }
}
     ''', 1, 4)
]


@pytest.mark.parametrize('pattern_type,file_name,patch_str,expected_length,line_no', params)
def test(pattern_type: str, file_name: str, patch_str: str, expected_length: int, line_no: int):
    patch = parse(patch_str, False)
    patch.name = file_name
    engine = DefaultEngine(included_filter=('BadMonthDetector', 'OverwrittenIncrementDetector'))
    engine.visit(patch)
    if expected_length > 0:
        assert len(engine.bug_accumulator) == expected_length
        assert engine.bug_accumulator[0].line_no == line_no
        assert engine.bug_accumulator[0].type == pattern_type
    else:
        assert len(engine.bug_accumulator) == 0
