import pytest

from patterns.detect.naming import Naming
from rparser import Patch

params = [
    # https://github.com/tesshucom/jpsonic/commit/04425589726efad5532e5828326f2de38e643cb1
    (Naming(), 'NM_SAME_SIMPLE_NAME_AS_SUPERCLASS', 'AirsonicSpringLiquibase.java',
        '''@@ -15,8 +15,9 @@
        import java.sql.Connection;
        import java.util.List;
        
        public class SpringLiquibase extends liquibase.integration.spring.SpringLiquibase''', 1, 18)
]

@pytest.mark.parametrize('detector,pattern_type,file_name,patch_str,expected_length,line_no', params)
def test(detector, pattern_type:str, file_name: str, patch_str: str, expected_length: int, line_no: int):
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