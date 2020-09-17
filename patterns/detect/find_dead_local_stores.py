import patterns.priorities as Priorities
from patterns.detectors import ParentDetector
from patterns.detectors import SubDetector
from patterns.bug_instance import BugInstance
import regex


class FindDeadLocalStoreMethods(ParentDetector):
    def __init__(self):
        ParentDetector.__init__(self, [
            FindLocalIncrementInReturnDetector()
        ])


class FindLocalIncrementInReturnDetector(SubDetector):
    def __init__(self):
        self.pattern = regex.compile('return\s+[A-Za-z_\$][A-Za-z_\$0-9]*(\+\+|\-\-)\s*;')
        SubDetector.__init__(self)

    def match(self, linecontent: str, filename: str, lineno: int):
        m = self.pattern.search(linecontent)
        if m:
            self.bug_accumulator.append(
                BugInstance("DLS_DEAD_LOCAL_INCREMENT_IN_RETURN", Priorities.NORMAL_PRIORITY, filename,
                            lineno, 'Useless increment in return statement')
            )
