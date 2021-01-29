import pytest

from patterns.models.engine import DefaultEngine
from rparser import parse

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
+public class AirsonicLocaleResolver implements org.springframework.web.servlet.LocaleResolver {''', 1, 42),
    # From other repository: https://github.com/hashbase/hashbase/commit/c47511baa7a8e50cecc9296f685b49249174cc77
    (True, 'NM_SAME_SIMPLE_NAME_AS_INTERFACE', 'Future.java',
     '''@@ -26,6 +26,9 @@
 */
@InterfaceAudience.Public
@InterfaceStability.Evolving
public interface Future<V> extends io.netty.util.concurrent.Future<V> {''', 1, 29),
    # DIY
    (False, 'NM_SAME_SIMPLE_NAME_AS_INTERFACE', 'AirsonicLocaleResolver.java',
     '''public class LocaleResolver extends DIYClass implements DIYInterface, org.springframework.web.servlet.LocaleResolver {''',
     1, 1),
    # DIY
    (True, 'NM_SAME_SIMPLE_NAME_AS_INTERFACE', 'Future.java',
     '''@@ -26,6 +26,9 @@
*/
@InterfaceAudience.Public
@InterfaceStability.Evolving
public interface Future<V> extends DIYInterface, io.netty.util.concurrent.Future<V> {''', 1, 29),
    # https://github.com/elastic/elasticsearch/blob/master/plugins/analysis-icu/src/main/java/org/elasticsearch/index/mapper/ICUCollationKeywordFieldMapper.java#L188
    (False, 'NM_SAME_SIMPLE_NAME_AS_SUPERCLASS', 'ICUCollationKeywordFieldMapper.java',
     '''public class ICUCollationKeywordFieldMapper extends FieldMapper {
    public static final String CONTENT_TYPE = "icu_collation_keyword";

    public static class Builder extends FieldMapper.Builder {
        final Parameter<Boolean> indexed = Parameter.indexParam(m -> toType(m).indexed, true);
        final Parameter<Boolean> hasDocValues = Parameter.docValuesParam(m -> toType(m).hasDocValues, true);''', 0, 4),
    # elasticsearch/x-pack/plugin/core/src/main/java/org/elasticsearch/xpack/core/async/AsyncResponse.java
    (False, 'NM_SAME_SIMPLE_NAME_AS_INTERFACE', 'AsyncResponse.java',
     '''public interface AsyncResponse<T extends AsyncResponse<?>> extends Writeable {
    /**
     * When this response will expire as a timestamp in milliseconds since epoch.
     */
    long getExpirationTime();''', 0, 1),
    # RxJava/src/main/java/io/reactivex/rxjava3/observers/BaseTestConsumer.java
    (False, 'NM_SAME_SIMPLE_NAME_AS_SUPERCLASS', 'BaseTestConsumer.java',
     '''public abstract class BaseTestConsumer<T, U extends BaseTestConsumer<T, U>> {''', 0, 1),
    # ------------------------ NM_LCASE_HASHCODE ------------------------
    # DIY
    (False, 'NM_LCASE_HASHCODE', 'Main_01.java',
     '''public class Main {
            int hashcode(){
                return 1;
            }
        }''', 1, 2),
    # DIY
    (False, 'NM_LCASE_HASHCODE', 'Main_02.java',
     '''public class Main {
            public int hashcode(){
                return 1;
            }
        }''', 1, 2),
    # DIY
    (False, 'NM_LCASE_HASHCODE', 'Main_03.java',
     '''public class Main {
            protected int hashcode(){
                return 1;
            }
        }''', 1, 2),

    (False, 'NM_LCASE_HASHCODE', 'Main_04.java',
         '''public final int hashcode(){
                    return 1;
                }''', 1, 1),
    (False, 'NM_LCASE_HASHCODE', 'Main_05.java',
         '''public int hashcode(int i){
                    return i;
                }''', 0, 1),
    (False, 'NM_LCASE_HASHCODE', 'Main_06.java',
     '''    private int hashcode(){
                return i;
            }''', 0, 1),
    # ------------------------ NM_LCASE_TOSTRING ------------------------
    # DIY
    (False, 'NM_LCASE_TOSTRING', 'Main_07.java',
     '''public class Main {
            String tostring(){
                return 1;
            }
        }''', 1, 2),
    # DIY
    (False, 'NM_LCASE_TOSTRING', 'Main_08.java',
     '''public class Main {
            public String tostring(){
                return 1;
            }
        }''', 1, 2),
    # DIY
    (False, 'NM_LCASE_TOSTRING', 'Main_09.java',
     '''public class Main {
            protected String tostring(){
                return 1;
            }
        }''', 1, 2),
    (False, 'NM_LCASE_TOSTRING', 'Main_10.java',
     '''     public static final String tostring(){''', 1, 1),
    # ------------------------ NM_BAD_EQUAL ------------------------
    (False, 'NM_BAD_EQUAL', 'Main_11.java', '''private boolean equal(Obejct o){''', 0, 1),
    (False, 'NM_BAD_EQUAL', 'Main_12.java', '''boolean equal(String s){''', 0, 1),
    (False, 'NM_BAD_EQUAL', 'Main_12.java', '''boolean equal( Object o ){''', 1, 1),
    (False, 'NM_BAD_EQUAL', 'Main_12.java', '''static boolean equal(Object o )''', 1, 1),
    # ------------------------ NM_FIELD_NAMING_CONVENTION ------------------------
    (False, 'NM_FIELD_NAMING_CONVENTION', 'Main_40.java', '''this.Field = field;''', 1, 1),
    (False, 'NM_FIELD_NAMING_CONVENTION', 'Main_41.java', '''this.FIELD = field;''', 0, 1),
    (False, 'NM_FIELD_NAMING_CONVENTION', 'Main_42.java', '''this.My_FIELD''', 0, 1),
    (False, 'NM_FIELD_NAMING_CONVENTION', 'Main_43.java',
     '''public class SpringLiquibase extends liquibase.integration.spring.CLASS{''', 0, 1),
    (False, 'NM_FIELD_NAMING_CONVENTION', 'Main_44.java', '''@InterfaceAudience.Public''', 0, 1),
    (False, 'NM_FIELD_NAMING_CONVENTION', 'Main_45.java', '''b = a.get();''', 0, 1),
    (False, 'NM_FIELD_NAMING_CONVENTION', 'Main_46.java', '''b = obj1.FieldOne.field;''', 1, 1),
    (False, 'NM_FIELD_NAMING_CONVENTION', 'Main_47.java', '''b = obj1.get().field;''', 0, 1),
]


@pytest.mark.parametrize('is_patch,pattern_type,file_name,patch_str,expected_length,line_no', params)
def test(is_patch: bool, pattern_type: str, file_name: str, patch_str: str, expected_length: int, line_no: int):
    patch = parse(patch_str, is_patch)
    patch.name = file_name

    engine = DefaultEngine(included_filter=['SimpleSuperclassNameDetector', 'SimpleInterfaceNameDetector',
                                            'HashCodeNameDetector', 'ToStringNameDetector', 'EqualNameDetector',
                                            'FieldNameConventionDetector',])
    engine.visit(patch)

    if expected_length > 0:
        assert len(engine.bug_accumulator) == expected_length
        assert engine.bug_accumulator[0].line_no == line_no
        assert engine.bug_accumulator[0].type == pattern_type
    else:
        assert len(engine.bug_accumulator) == 0
