import regex

from patterns.models.bug_instance import BugInstance
from patterns.models.detectors import Detector
import patterns.models.priorities as Priorities


class CheckForSelfComputation(Detector):
    def __init__(self):
        self.pattern = regex.compile(r'(\b\w[\w.]*(?P<aux1>\((?:[^()]++|(?&aux1))*\))*+)\s*([|^&-])\s*\1[^.\w$]')
        Detector.__init__(self)

    def match(self, linecontent: str, filename: str, lineno: int, **kwargs):
        if not any(op in linecontent for op in ('&', '|', '^', '-')):
            return

        its = self.pattern.finditer(linecontent)
        for m in its:
            self.bug_accumulator.append(
                BugInstance('SA_SELF_COMPUTATION', Priorities.MEDIUM_PRIORITY, filename, lineno,
                            'Nonsensical self computation')
            )
