import re

from patterns.detectors import ParentDetector, SubDetector
from patterns.bug_instance import BugInstance
import patterns.priorities as Priorities


class FindFinalizeInvocations(ParentDetector):
    def __init__(self):
        ParentDetector.__init__(self, [
            ExplicitInvSubDetector(),
            PublicAccessSubDetector()
        ])


class ExplicitInvSubDetector(SubDetector):
    def __init__(self):
        self.pattern = re.compile('\.finalize\s*\(\s*\)\s*;')
        SubDetector.__init__(self)

    def match(self, linecontent: str, filename: str, lineno: int):
        m = self.pattern.search(linecontent)
        if m:
            self.bug_accumulator.append(
                BugInstance('FI_EXPLICIT_INVOCATION', Priorities.HIGH_PRIORITY, filename, lineno,
                            'Explicit invocation of Object.finalize()')
            )


class PublicAccessSubDetector(SubDetector):
    def __init__(self):
        self.pattern = re.compile('public\s+void\s+finalize\(\s*\)')
        SubDetector.__init__(self)

    def match(self, linecontent: str, filename: str, lineno: int):
        m = self.pattern.search(linecontent)
        if m:
            self.bug_accumulator.append(
                BugInstance('FI_PUBLIC_SHOULD_BE_PROTECTED', Priorities.NORMAL_PRIORITY, filename, lineno,
                            'Finalizer should be protected, not public')
            )
