import regex

from patterns.detectors import ParentDetector, SubDetector
from patterns.bug_instance import BugInstance
import patterns.priorities as Priorities


class Naming(ParentDetector):
    def __init__(self):
        ParentDetector.__init__(self, [
            SimpleNameSubDetector1()
        ])


class SimpleNameSubDetector1(SubDetector):
    def __init__(self):
        self.pattern = regex.compile(r'class\s+(\w+)\s+extends\s+([\w\.]+)')
        SubDetector.__init__(self)

    def match(self, linecontent: str, filename: str, lineno: int):
        m = self.pattern.search(linecontent)
        if m:
            g = m.groups()
            class_name = g[0]
            super_class_name = g[1].split('.')[-1]

            if class_name == super_class_name:
                self.bug_accumulator.append(
                    BugInstance('NM_SAME_SIMPLE_NAME_AS_SUPERCLASS', Priorities.HIGH_PRIORITY, filename, lineno,
                                'Class names shouldn’t shadow simple name of superclass')
                )