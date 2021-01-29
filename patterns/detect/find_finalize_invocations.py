import re

from patterns.models.detectors import Detector
from patterns.models.bug_instance import BugInstance
from patterns.models import priorities


class ExplicitInvDetector(Detector):
    def __init__(self):
        self.pattern = re.compile(r'(\b\w+)\.finalize\s*\(\s*\)\s*;')
        Detector.__init__(self)

    def match(self, context):
        line_content = context.cur_line.content
        m = self.pattern.search(line_content.strip())
        if m and m.groups()[0] != 'super':
            self.bug_accumulator.append(
                BugInstance('FI_EXPLICIT_INVOCATION', priorities.HIGH_PRIORITY, context.cur_patch.name,
                            context.cur_line.lineno[1],
                            'Explicit invocation of Object.finalize()')
            )


class PublicAccessDetector(Detector):
    def __init__(self):
        self.pattern = re.compile(r'public\s+void\s+finalize\s*\(\s*\)')
        Detector.__init__(self)

    def match(self, context):
        line_content = context.cur_line.content
        m = self.pattern.search(line_content.strip())
        if m:
            self.bug_accumulator.append(
                BugInstance('FI_PUBLIC_SHOULD_BE_PROTECTED', priorities.MEDIUM_PRIORITY, context.cur_patch.name,
                            context.cur_line.lineno[1],
                            'Finalizer should be protected, not public')
            )
