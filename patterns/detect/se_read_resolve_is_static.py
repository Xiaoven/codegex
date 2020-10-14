import re
from patterns.detectors import ParentDetector, SubDetector
from patterns.bug_instance import BugInstance
import patterns.priorities as Priorities

class SeReadResolveIsStatic(ParentDetector):
    def __init__(self):
        ParentDetector.__init__(self, [
            WhetherThereIsStatic()
        ])

class WhetherThereIsStatic(SubDetector):
    def __init__(self):
        self.pattern = re.compile(r'(s{0,1}t{0,1}a{0,1}t{0,1}i{0,1}c{0,1}\s+Object)\s+(readResolve\(\))')
        SubDetector.__init__(self)

    def match(self, linecontent: str, filename: str, lineno: int):
        m = self.pattern.search(linecontent)
        if m:
            g = m.groups()
            assert len(g) == 2
            obj = g[0].split()
            if 'static' in obj:
                self.bug_accumulator.append(
                    BugInstance('SE_READ_RESOLVE_IS_STATIC', Priorities.NORMAL_PRIORITY, filename,
                                lineno,
                                'The readResolve method must not be declared as a static method')
                )