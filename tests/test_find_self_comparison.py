import pytest

from patterns.models.engine import DefaultEngine
from rparser import parse

params = [
    # https://github.com/mhagnumdw/bean-info-generator/pull/5/files#diff-71bf0b35fa483782180f548a1a7d6cc4b3822ed12aa4bb86640f80dde9df3077R13
    (False, 'SA_SELF_COMPUTATION', 'Ideas_2013_11_06.java ',
     '''@NoWarning("SA_FIELD_SELF_COMPUTATION")
        public int testUpdate() {
            return flags ^(short) flags;
        }''', 0, 1),
    # https://github.com/spotbugs/spotbugs/blob/3883a7b750fb339577be073bc45e36b6f268777b/spotbugsTestCases/src/java/SelfFieldOperation.java#L25
    (False, 'SA_SELF_COMPUTATION', 'SelfFieldOperation.java',
     '''@ExpectWarning("SA_FIELD_SELF_COMPARISON,SA_FIELD_SELF_COMPUTATION")
        int f() {
            if (x < x)
                x = (int) ( y ^ y);
            if (x != x)
                y = x | x;
            if (x >= x)
                x = (int)(y & y);
            if (y > y)
                y = x - x;
            return x;
        }''', 8, 3),
    # DIY
    (False, 'SA_SELF_COMPUTATION', 'DIY_01.java',
     '''return capabilities.level - level;''', 0, 1),
    # ---------------- SA_SELF_COMPARISON ----------------------
    (False, 'SA_SELF_COMPARISON', 'SelfFieldOperation.java',
     '''@NoWarning("SA_FIELD_SELF_COMPARISON")
        public boolean test() {
            boolean result = false;
            result |= flags == (short) flags;
            result |= flags == (char) flags;
            result |= flags == (byte) flags;
            return result;
        }''', 0, 3),
    (False, 'SA_SELF_COMPARISON', 'SelfFieldOperation.java',
     '''@ExpectWarning("SA_FIELD_SELF_COMPARISON")
        public boolean testTP() {
            boolean result = false;
            result |= flags == flags;
            return result;
        }''', 1, 4),
    (False, 'SA_SELF_COMPARISON', 'SelfFieldOperation.java',
     '''@ExpectWarning(value="SA_FIELD_SELF_COMPARISON", confidence = Confidence.LOW)
    boolean volatileFalsePositive() {
        return z == z;
    }''', 1, 3),
    (False, 'SA_SELF_COMPARISON', 'SelfFieldOperation.java',
     '''@ExpectWarning("SA_FIELD_SELF_COMPARISON")
        boolean e() {
            return a.equals(a);
        }''', 1, 3),
    (False, 'SA_SELF_COMPARISON', 'SelfFieldOperation.java',
     '''@ExpectWarning("SA_FIELD_SELF_COMPARISON")
        int c() {
            return a.compareTo(a);
        }
    ''', 1, 3),
    (False, 'SA_SELF_COMPARISON', 'SelfFieldOperation.java',
     ''' Objects.equals(requestCount, throttlingPolicy.requestCount) &&
         Objects.equals(unitTime, throttlingPolicy.unitTime) &&
         Objects.equals(timeUnit, throttlingPolicy.timeUnit) &&
         Objects.equals(tierPlan, throttlingPolicy.tierPlan) &&
         Objects.equals(stopOnQuotaReach, throttlingPolicy.stopOnQuotaReach) &&
         Objects.equals(monetizationProperties, throttlingPolicy.monetizationProperties);''', 0, 1),
    #  https://github.com/google/ExoPlayer/pull/8462
    (False, 'SA_SELF_COMPARISON', '', 'if (capabilities.profile == profile && capabilities.level >= level) { ', 0, 1)
]


@pytest.mark.parametrize('is_patch,pattern_type,file_name,patch_str,expected_length,line_no', params)
def test(is_patch: bool, pattern_type: str, file_name: str, patch_str: str, expected_length: int, line_no: int):
    patch = parse(patch_str, is_patch)
    engine = DefaultEngine(included_filter=['CheckForSelfComputation', 'CheckForSelfComparison'])
    engine.visit(patch)
    if expected_length > 0:
        assert len(engine.bug_accumulator) == expected_length
        assert engine.bug_accumulator[0].line_no == line_no
        assert engine.bug_accumulator[0].type == pattern_type
    else:
        assert len(engine.bug_accumulator) == 0
