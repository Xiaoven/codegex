import regex

from patterns.detectors import ParentDetector, SubDetector
from patterns.bug_instance import BugInstance
import patterns.priorities as Priorities


class MethodReturnCheck(ParentDetector):
    def __init__(self):
        ParentDetector.__init__(self, [
            NotThrowSubDetector()
        ])


class NotThrowSubDetector(SubDetector):
    def __init__(self):
        super().__init__()
        self.pattern = regex.compile(r'^\s*new\s+(\w+)(?:Exception|Error)\s*\(')

    def match(self, linecontent: str, filename: str, lineno: int, get_exact_lineno=None):
        m = self.pattern.search(linecontent)
        if m:
            self.bug_accumulator.append(
                BugInstance('RV_EXCEPTION_NOT_THROWN', Priorities.NORMAL_PRIORITY,
                            filename, lineno,
                            "Exception created and dropped rather than thrown")
            )