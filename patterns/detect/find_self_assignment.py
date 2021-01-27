import regex

from patterns.models.bug_instance import BugInstance
from patterns.models.detectors import Detector
import patterns.models.priorities as Priorities

class CheckForSelfAssignment(Detector):
    def __init__(self):
        self.pattern = regex.compile(r'(\b(\w[\w.]*))\s*=\s*(\1)\s*;')
        Detector.__init__(self)

    def match(self, linecontent: str, filename: str, lineno: int, **kwargs):
        strip_line = linecontent.strip()
        if '=' in linecontent and self.pattern.search(strip_line):
            self.bug_accumulator.append(
                BugInstance('SA_SELF_ASSIGNMENT', Priorities.HIGH_PRIORITY, filename, lineno,
                            'SA: Self assignment of field or variable')
            )