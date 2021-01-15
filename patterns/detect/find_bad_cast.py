import regex
from patterns.models.bug_instance import BugInstance
from patterns.models.detectors import Detector
from patterns.models import priorities


class FindBadCastDetector(Detector):
    def __init__(self):
        self.pattern = regex.compile(
            r'\(\s*(\w+)\s*\[\s*\]\s*\)\s*((?:(?P<aux1>\((?:[^()]++|(?&aux1))*\))|[\w.$<>\s])+?)\s*\.\s*toArray\s*\(\s*\)')
        Detector.__init__(self)

    def match(self, linecontent: str, filename: str, lineno: int, **kwargs):
        if 'toArray' not in linecontent:
            return

        its = self.pattern.finditer(linecontent)
        for m in its:
            g = m.groups()
            type_name = g[0]
            obj_name = g[1]

            if g[0] != 'Object' and 'Arrays.asList' not in linecontent:
                self.bug_accumulator.append(
                    BugInstance('BC_IMPOSSIBLE_DOWNCAST_OF_TOARRAY', priorities.HIGH_PRIORITY,
                                filename, lineno,
                                "BC: Impossible downcast of toArray() result")
                )

