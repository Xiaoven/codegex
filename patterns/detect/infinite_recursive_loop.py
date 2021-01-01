import regex

from patterns.models.detectors import Detector
from patterns.models.bug_instance import BugInstance
import patterns.priorities as Priorities


class CollectionAddItselfDetector(Detector):
    def __init__(self):
        self.pattern = regex.compile(r'(\b\w[\w.]*(?P<aux1>\((?:[^()]++|(?&aux1))*\))*+)\s*\.\s*add\s*\(\s*\1\s*\)')
        Detector.__init__(self)

    def match(self, linecontent: str, filename: str, lineno: int, get_exact_lineno=None):
        if "add" not in linecontent:
            return
        m = self.pattern.search(linecontent.strip())
        if m:
            self.bug_accumulator.append(
                BugInstance('IL_CONTAINER_ADDED_TO_ITSELF', Priorities.HIGH_PRIORITY, filename,
                            lineno,
                            'A collection is added to itself')
            )
