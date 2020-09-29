import re
from patterns.detectors import ParentDetector, SubDetector
from patterns.bug_instance import BugInstance
import patterns.priorities as Priorities

class JcipFieldIsntFinalInImmutableClass(ParentDetector):
    def __init__(self):
        ParentDetector.__init__(self, [
            WhetherThereIsFinal()
        ])

class WhetherThereIsFinal(SubDetector):
    def __init__(self):
        self.pattern = re.compile(r'(f{0,1}i{0,1}n{0,1}a{0,1}l{0,1}\s+class\s+.*implements).*(String|Double|BigInteger|BigDecimal|Integer|Long|Float|Short|Byte|Charater|Boolean)')
        SubDetector.__init__(self)

    def match(self, linecontent: str, filename: str, lineno: int):
        m = self.pattern.search(linecontent)
        if m:
            g = m.groups()
            assert len(g) == 2
            obj = g[0].split()
            if 'final' in obj:
                return
            else:
                self.bug_accumulator.append(
                    BugInstance('JCIP_FIELD_ISNT_FINAL_IN_IMMUTABLE_CLASS', Priorities.NORMAL_PRIORITY, filename,
                                lineno,
                                'Fields of immutable classes should be final')
                )