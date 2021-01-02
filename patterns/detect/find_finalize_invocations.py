import re

from patterns.models.detectors import Detector
from patterns.models.bug_instance import BugInstance
from patterns.models import priorities


class ExplicitInvDetector(Detector):
    def __init__(self):
        self.pattern = re.compile(r'(\b\w+)\.finalize\s*\(\s*\)\s*;')
        Detector.__init__(self)

    def match(self, linecontent: str, filename: str, lineno: int, **kwargs):
        m = self.pattern.search(linecontent.strip())
        if m and m.groups()[0] != 'super':
            self.bug_accumulator.append(
                BugInstance('FI_EXPLICIT_INVOCATION', priorities.HIGH_PRIORITY, filename, lineno,
                            'Explicit invocation of Object.finalize()')
            )


class PublicAccessDetector(Detector):
    def __init__(self):
        self.pattern = re.compile(r'public\s+void\s+finalize\s*\(\s*\)')
        Detector.__init__(self)

    def match(self, linecontent: str, filename: str, lineno: int, **kwargs):
        m = self.pattern.search(linecontent.strip())
        if m:
            self.bug_accumulator.append(
                BugInstance('FI_PUBLIC_SHOULD_BE_PROTECTED', priorities.MEDIUM_PRIORITY, filename, lineno,
                            'Finalizer should be protected, not public')
            )
