import regex

from patterns.detectors import Detector
from patterns.bug_instance import BugInstance
import patterns.priorities as Priorities


def clearName(dotted_name: str):
    name = dotted_name.rsplit('<', 1)[0]  # remove generics like '<T>'
    name = name.rsplit('.', 1)[-1]  # remove package
    return name.strip()


class SimpleNameDetector1(Detector):
    def __init__(self):
        self.pattern = regex.compile(r'class\s+((?P<name>[\w.\s<>,])+?)\s+extends\s+((?:(?!implements)(?&name))+)')
        Detector.__init__(self)

    def match(self, linecontent: str, filename: str, lineno: int, get_exact_lineno=None):
        m = self.pattern.search(linecontent)
        if m:
            g = m.groups()
            class_name = clearName(g[0])
            super_class_name = clearName(g[2])

            if class_name == super_class_name:
                self.bug_accumulator.append(
                    BugInstance('NM_SAME_SIMPLE_NAME_AS_SUPERCLASS', Priorities.HIGH_PRIORITY, filename, lineno,
                                "Class names shouldn’t shadow simple name of superclass")
                )


class SimpleNameDetector2(Detector):
    def __init__(self):
        self.pattern1 = regex.compile(
            r'class\s+((?:(?!extends)(?P<name>[\w.\s<>,]))+?)\s+(?&name)*?\bimplements\s+((?&name)+)')
        self.pattern2 = regex.compile(r'interface\s+((?P<name>[\w.\s<>,])+?)\s+extends\s+((?&name)+)')
        Detector.__init__(self)

    def match(self, linecontent: str, filename: str, lineno: int, get_exact_lineno=None):
        m = self.pattern1.search(linecontent)
        if not m:
            m = self.pattern2.search(linecontent)

        if m:
            g = m.groups()
            class_name = clearName(g[0])  # skip g[1] that is matched by (?P<name>)
            interface_names = []
            for itf in g[2].split(','):
                interface_names.append(clearName(itf))

            if class_name in interface_names:
                self.bug_accumulator.append(
                    BugInstance('NM_SAME_SIMPLE_NAME_AS_INTERFACE', Priorities.NORMAL_PRIORITY, filename, lineno,
                                "Class or interface names shouldn’t shadow simple name of implemented interface")
                )
