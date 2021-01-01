import regex

from patterns.models.detectors import Detector
from patterns.models.bug_instance import BugInstance
import patterns.priorities as Priorities


class NotThrowDetector(Detector):
    def __init__(self):
        super().__init__()
        self.pattern = regex.compile(r'^\s*new\s+(\w+?)(?:Exception|Error)\s*\(')

    def match(self, linecontent: str, filename: str, lineno: int, get_exact_lineno=None):
        m = self.pattern.search(linecontent.strip())
        if m:
            self.bug_accumulator.append(
                BugInstance('RV_EXCEPTION_NOT_THROWN', Priorities.MEDIUM_PRIORITY,
                            filename, lineno,
                            "Exception created and dropped rather than thrown")
            )