import regex as re

from patterns.bug_instance import BugInstance
from patterns.detectors import ParentDetector, SubDetector
import patterns.priorities as Priorities


class SelfComputation(ParentDetector):
    def __init__(self):
        ParentDetector.__init__(self, [
            SelfComputationSubDetector()
        ])


class SelfComputationSubDetector(SubDetector):
    def __init__(self):
        self.pattern = re.compile(r'([\w_\.]+(?:(?P<aux1>\((?:[^()]++|(?&aux1))*\)))*+)\s*[\^\&\|\-]\s*\1\s*')
        SubDetector.__init__(self)

    def match(self, linecontent: str, filename: str, lineno: int, get_exact_lineno=None):
        m = self.pattern.search(linecontent)
        if m:
            self.bug_accumulator.append(
                BugInstance('SA_SELF_COMPUTATION', Priorities.NORMAL_PRIORITY, filename, lineno,
                            'Nonsensical self computation')
            )
