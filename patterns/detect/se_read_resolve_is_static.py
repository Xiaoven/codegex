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
        self.pattern = re.compile(r'(static)?\s*Object\s+readResolve\(\)\s+throws\s+ObjectStreamException')
        SubDetector.__init__(self)

    def match(self, linecontent: str, filename: str, lineno: int):
        m = self.pattern.search(linecontent)
        if m:
            g = m.groups()
            
            
            if 'static' in g:
                self.bug_accumulator.append(
                    BugInstance('SE_READ_RESOLVE_IS_STATIC', Priorities.HIGH_PRIORITY, filename,
                                lineno,
                                'The readResolve method must not be declared as a static method')
                )