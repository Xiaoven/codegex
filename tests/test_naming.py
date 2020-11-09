import pytest

from patterns.detect.naming import Naming
from rparser import Patch, parse

params = [
    # From other repository: https://github.com/tesshucom/jpsonic/commit/04425589726efad5532e5828326f2de38e643cb1
    (True, 'NM_SAME_SIMPLE_NAME_AS_SUPERCLASS', 'AirsonicSpringLiquibase.java',
     '''@@ -15,8 +15,9 @@
        import java.sql.Connection;
        import java.util.List;

        public class SpringLiquibase extends liquibase.integration.spring.SpringLiquibase''', 1, 18),
    # DIY from: https://github.com/makotoarakaki/aipo/commit/b4eae261c527a41af1ade5b1d1fa95548f9a36cc
    (True, 'NM_SAME_SIMPLE_NAME_AS_SUPERCLASS', 'ALActivityImpl.java',
     '''@@ -29,8 +29,9 @@
    public class ALActivityImpl extends org.apache.shindig.social.core.model.ALActivityImpl implements Activity {''', 1, 29),
    # From other repository: https://github.com/tesshucom/jpsonic/commit/e82450ff9e8cd81ac0122de9f268f36c68683464
    (True, 'NM_SAME_SIMPLE_NAME_AS_INTERFACE', 'AirsonicLocaleResolver.java',
     '''@@ -39,7 +39,7 @@
         * @author Sindre Mehus
         */
        @Service
        public class LocaleResolver implements org.springframework.web.servlet.LocaleResolver {
        + public class AirsonicLocaleResolver implements org.springframework.web.servlet.LocaleResolver {''', 1, 42),
    # From other repository: https://github.com/hashbase/hashbase/commit/c47511baa7a8e50cecc9296f685b49249174cc77
    (True, 'NM_SAME_SIMPLE_NAME_AS_INTERFACE', 'Future.java',
     '''@@ -26,6 +26,9 @@
         */
        @InterfaceAudience.Public
        @InterfaceStability.Evolving
        public interface Future<V> extends io.netty.util.concurrent.Future<V> {''', 1, 29),
    # DIY
    (True, 'NM_SAME_SIMPLE_NAME_AS_INTERFACE', 'AirsonicLocaleResolver.java',
     '''@@ -39,7 +39,7 @@
     * @author Sindre Mehus
     */
    @Service
    public class LocaleResolver extends DIYClass implements DIYInterface, org.springframework.web.servlet.LocaleResolver {''',
     1, 42),
    # DIY
    (True, 'NM_SAME_SIMPLE_NAME_AS_INTERFACE', 'Future.java',
     '''@@ -26,6 +26,9 @@
         */
        @InterfaceAudience.Public
        @InterfaceStability.Evolving
        public interface Future<V> extends DIYInterface, io.netty.util.concurrent.Future<V> {''', 1, 29),
]


@pytest.mark.parametrize('is_patch,pattern_type,file_name,patch_str,expected_length,line_no', params)
def test(is_patch: bool, pattern_type: str, file_name: str, patch_str: str, expected_length: int, line_no: int):
    patch = parse(patch_str, is_patch)
    patch.name = file_name
    detector = Naming()
    detector.visit([patch])
    if expected_length > 0:
        assert len(detector.bug_accumulator) == expected_length
        assert detector.bug_accumulator[0].line_no == line_no
        assert detector.bug_accumulator[0].type == pattern_type
    else:
        assert len(detector.bug_accumulator) == 0
