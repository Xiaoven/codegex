import regex

from patterns.models.bug_instance import BugInstance
from patterns.models.detectors import Detector
import patterns.models.priorities as Priorities


class CheckForSelfAssignment(Detector):
    def __init__(self):
        self.pattern = regex.compile(r'(\b\w[\w.]*)\s*=\s*(\w[\w.]*)\s*;')
        Detector.__init__(self)

    def match(self, context):
        strip_line = context.cur_line.content.strip()
        if '=' in strip_line:
            m = self.pattern.search(strip_line)
            if m:
                g = m.groups()
                if g[0] == g[1]:
                    self.bug_accumulator.append(
                        BugInstance('SA_SELF_ASSIGNMENT', Priorities.HIGH_PRIORITY, context.cur_patch.name,
                                    context.cur_line.lineno[1],
                                    'SA: Self assignment of field or variable', sha=context.cur_patch.sha)
                    )


class CheckForSelfDoubleAssignment(Detector):
    def __init__(self):
        self.pattern = regex.compile(r'\b(\w[\w.]*)\s*=\s*(\w[\w.]*)\s*=[^=]')
        Detector.__init__(self)

    def match(self, context):
        strip_line = context.cur_line.content.strip()
        if '=' in strip_line:
            m = self.pattern.search(strip_line)
            if m:
                g = m.groups()
                if g[0] == g[1]:
                    self.bug_accumulator.append(
                        BugInstance('SA_DOUBLE_ASSIGNMENT', Priorities.HIGH_PRIORITY, context.cur_patch.name,
                                    context.cur_line.lineno[1],
                                    'SA: Double assignment of field or local variable', sha=context.cur_patch.sha)
                    )
