import regex

from patterns.models.detectors import Detector
from patterns.models.bug_instance import BugInstance
from patterns.models import priorities


class NotThrowDetector(Detector):
    def __init__(self):
        super().__init__()
        self.pattern = regex.compile(r'^\s*new\s+(\w+?)(?:Exception|Error)\s*\(')

    def match(self, context):
        m = self.pattern.search(context.cur_line.content.strip())
        if m:
            self.bug_accumulator.append(
                BugInstance('RV_EXCEPTION_NOT_THROWN', priorities.MEDIUM_PRIORITY,
                            context.cur_patch.name, context.cur_line.lineno[1],
                            "Exception created and dropped rather than thrown")
            )