import regex

from patterns.models.detectors import Detector
from patterns.models.bug_instance import BugInstance
from patterns.models import priorities


class CollectionAddItselfDetector(Detector):
    def __init__(self):
        self.pattern = regex.compile(
            r'(\b\w[\w.]*(?P<aux1>\((?:[^()]++|(?&aux1))*\))*+)\s*\.\s*add\s*\(\s*([\w.]+(?&aux1)*)\s*\)')
        Detector.__init__(self)

    def match(self, linecontent: str, filename: str, lineno: int, **kwargs):
        if "add" not in linecontent:
            return
        its = self.pattern.finditer(linecontent.strip())
        for m in its:
            g = m.groups()
            if g[0] == g[2]:
                self.bug_accumulator.append(
                    BugInstance('IL_CONTAINER_ADDED_TO_ITSELF', priorities.HIGH_PRIORITY, filename,
                                lineno,
                                'A collection is added to itself')
                )
