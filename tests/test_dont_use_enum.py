import pytest

from patterns.models.context import Context
from rparser import parse
from patterns.models.engine import DefaultEngine

params = [
    # DIY
    ('NM_FUTURE_KEYWORD_USED_AS_IDENTIFIER', 'Main00.java',
     '''public Main00.java{
    int assert = 0;
}
     ''', 1, 2),
    ('NM_FUTURE_KEYWORD_USED_AS_IDENTIFIER', 'Main01.java',
     '''public Main01.java{
    public enum Day {
    SUNDAY, MONDAY, TUESDAY, WEDNESDAY,
    THURSDAY, FRIDAY, SATURDAY 
    }
}
     ''', 0, 1),
    ('NM_FUTURE_KEYWORD_USED_AS_IDENTIFIER', 'Main02.java',
     '''public Main02.java{
    String enum = "hello world";
}
     ''', 1, 2),
    ('NM_FUTURE_KEYWORD_USED_AS_MEMBER_IDENTIFIER', 'Main03.java',
     '''public Main03.java{
    void enum(){
    ;
    }
}
     ''', 1, 2),
    ('NM_FUTURE_KEYWORD_USED_AS_MEMBER_IDENTIFIER', 'Main03.java',
     '''public Main04.java{
    private String assert(int num1, int num2){
        return null;
    }
}
     ''', 1, 2),
    ('NM_FUTURE_KEYWORD_USED_AS_MEMBER_IDENTIFIER', 'Main03.java',
     '''public Main05.java{
    void test05(int num1, int num2){
        System.out.println(assert(num1=num2));
    }
}
     ''', 0, 1),
    ('NM_FUTURE_KEYWORD_USED_AS_IDENTIFIER', 'Main06.java',
     '''public enum Color
     ''', 0, 1),
    ('NM_FUTURE_KEYWORD_USED_AS_IDENTIFIER', 'Main06.java',
     '''int enum;
     ''', 1, 1),
    ('NM_FUTURE_KEYWORD_USED_AS_IDENTIFIER', 'Main06.java',
     '''if ( enum > 0){ ... }
     ''', 1, 1),
    ('NM_FUTURE_KEYWORD_USED_AS_IDENTIFIER', 'Main06.java',
     '''enum = 10;
     ''', 1, 1),
    ('NM_FUTURE_KEYWORD_USED_AS_IDENTIFIER', 'Main06.java',
     '''if( 3 < assert)
     ''', 1, 1),
    ('NM_FUTURE_KEYWORD_USED_AS_IDENTIFIER', 'Main06.java',
     '''while(assert && a)
     ''', 1, 1),
    ('NM_FUTURE_KEYWORD_USED_AS_MEMBER_IDENTIFIER', 'Main03.java',
     '''assert (a > 0);''', 0, 1),
    ('NM_FUTURE_KEYWORD_USED_AS_MEMBER_IDENTIFIER', 'Main03.java',
     '''a.enum(expression)''', 1, 1),
]

@pytest.mark.parametrize('pattern_type,file_name,patch_str,expected_length,line_no', params)
def test(pattern_type: str, file_name: str, patch_str: str, expected_length: int, line_no: int):
    patch = parse(patch_str, False)
    patch.name = file_name
    engine = DefaultEngine(Context(), included_filter=('DontUseEnumDetector',))
    engine.visit(patch)
    if expected_length > 0:
        assert len(engine.bug_accumulator) == expected_length
        assert engine.bug_accumulator[0].line_no == line_no
        assert engine.bug_accumulator[0].type == pattern_type
    else:
        assert len(engine.bug_accumulator) == 0