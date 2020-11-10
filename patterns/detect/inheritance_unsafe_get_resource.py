import re

from patterns.bug_instance import BugInstance
from patterns.detectors import ParentDetector, SubDetector
import patterns.priorities as Priorities


class InheritanceUnsafeGetResource(ParentDetector):
    def __init__(self):
        ParentDetector.__init__(self, [
            GetResourceSubDetector()
        ])


class GetResourceSubDetector(SubDetector):
    def __init__(self):
        self.pattern = re.compile(r'(\w*)\.*getClass\(\s*\)\.getResource(?:AsStream){0,1}\(')
        SubDetector.__init__(self)

    def match(self, linecontent: str, filename: str, lineno: int, get_exact_lineno=None):
        m = self.pattern.search(linecontent)
        if m:
            obj_name = m.groups()[0]
            if not obj_name or obj_name == 'this':
                self.bug_accumulator.append(
                    BugInstance('UI_INHERITANCE_UNSAFE_GETRESOURCE', Priorities.NORMAL_PRIORITY, filename, lineno,
                                'Usage of GetResource may be unsafe if class is extended')
                )
