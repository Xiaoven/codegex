import re

from patterns.bug_instance import BugInstance
from patterns.detectors import Detector
import patterns.priorities as Priorities


class GetResourceDetector(Detector):
    def __init__(self):
        self.pattern = re.compile(r'(?:(\b\w+)\.)?getClass\(\s*\)\.getResource(?:AsStream)?\(')
        Detector.__init__(self)

    def match(self, linecontent: str, filename: str, lineno: int, get_exact_lineno=None):
        if not all(method in linecontent for method in ['getClass', 'getResource']):
            return

        m = self.pattern.search(linecontent)
        if m:
            obj_name = m.groups()[0]
            if not obj_name or obj_name == 'this':
                self.bug_accumulator.append(
                    BugInstance('UI_INHERITANCE_UNSAFE_GETRESOURCE', Priorities.MEDIUM_PRIORITY, filename, lineno,
                                'Usage of GetResource may be unsafe if class is extended')
                )
