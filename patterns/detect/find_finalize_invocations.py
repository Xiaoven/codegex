import re

from patterns.detectors import Detector
from patterns.bug_instance import BugInstance
import patterns.priorities as Priorities


class ExplicitInvDetector(Detector):
    def __init__(self):
        self.pattern = re.compile(r'(\b\w+)\.finalize\s*\(\s*\)\s*;')
        Detector.__init__(self)

    def match(self, linecontent: str, filename: str, lineno: int, get_exact_lineno=None):
        m = self.pattern.search(linecontent.strip())
        if m and m.groups()[0] != 'super':
            self.bug_accumulator.append(
                BugInstance('FI_EXPLICIT_INVOCATION', Priorities.HIGH_PRIORITY, filename, lineno,
                            'Explicit invocation of Object.finalize()')
            )


class PublicAccessDetector(Detector):
    def __init__(self):
        self.pattern = re.compile(r'public\s+void\s+finalize\s*\(\s*\)')
        Detector.__init__(self)

    def match(self, linecontent: str, filename: str, lineno: int, get_exact_lineno=None):
        m = self.pattern.search(linecontent.strip())
        if m:
            self.bug_accumulator.append(
                BugInstance('FI_PUBLIC_SHOULD_BE_PROTECTED', Priorities.MEDIUM_PRIORITY, filename, lineno,
                            'Finalizer should be protected, not public')
            )
