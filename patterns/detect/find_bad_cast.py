import regex
from patterns.models.bug_instance import BugInstance
from patterns.models.detectors import Detector
from patterns.models import priorities


class FindBadCastDetector(Detector):
    def __init__(self):
        self.pattern = regex.compile(
            r'\(\s*(\w+)\s*\[\s*\]\s*\)\s*((?:(?P<aux1>\((?:[^()]++|(?&aux1))*\))|[\w.$<>\s])+?)\s*\.\s*toArray\s*\(\s*\)')
        Detector.__init__(self)

    def match(self, context):
        line_content = context.cur_line.content
        if 'toArray' not in line_content:
            return

        its = self.pattern.finditer(line_content)
        for m in its:
            g = m.groups()

            if g[0] != 'Object' and 'Arrays.asList' not in line_content:
                self.bug_accumulator.append(
                    BugInstance('BC_IMPOSSIBLE_DOWNCAST_OF_TOARRAY', priorities.HIGH_PRIORITY,
                                context.cur_patch.name, context.cur_line.lineno[1],
                                "BC: Impossible downcast of toArray() result")
                )

