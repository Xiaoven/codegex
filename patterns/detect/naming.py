import regex

from patterns.detectors import ParentDetector, SubDetector
from patterns.bug_instance import BugInstance
import patterns.priorities as Priorities


def clearName(dotted_name: str):
    name = dotted_name.rsplit('<', 1)[0]  # remove generics like '<T>'
    name = name.rsplit('.', 1)[-1]  # remove package
    return name.strip()


class Naming(ParentDetector):
    def __init__(self):
        ParentDetector.__init__(self, [
            SimpleNameSubDetector1(),
            SimpleNameSubDetector2(),
            typoOverrideDetector()
        ])


class SimpleNameSubDetector1(SubDetector):
    def __init__(self):
        self.pattern = regex.compile(r'class\s+((?P<name>[\w\.\s<>,])+)\s+extends\s+((?:(?!implements)(?&name))+)')
        SubDetector.__init__(self)

    def match(self, linecontent: str, filename: str, lineno: int):
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


class SimpleNameSubDetector2(SubDetector):
    def __init__(self):
        self.pattern1 = regex.compile(r'class\s+((?:(?!extends)(?P<name>[\w\.\s<>,]))+)\s+(?&name)*implements\s+((?&name)+)')
        self.pattern2 = regex.compile(r'interface\s+((?P<name>[\w\.\s<>,])+)\s+extends\s+((?&name)+)')
        SubDetector.__init__(self)

    def match(self, linecontent: str, filename: str, lineno: int):
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

class typoOverrideDetector(SubDetector):
    def __init__(self):
        self.pattern1 = regex.compile(
            r'public\s+int\s+hashcode\s*\(\s*\)')
        self.pattern2 = regex.compile(
            r'public\s+String\s+tostring\s*\(\s*\)')
        self.pattern3 = regex.compile(
            r'public\s+boolean\s+equal\s*\(\s*Object\s+\)'
        )
        SubDetector.__init__(self)

    def match(self, linecontent: str, filename: str, lineno: int):
        typoHash = self.pattern1.search(linecontent)
        typotoString = self.pattern2.search(linecontent)
        typoEquals = self.pattern3.search(linecontent)
        if typoHash:
            self.bug_accumulator.append(
                BugInstance('NM_LCASE_HASHCODE', Priorities.HIGH_PRIORITY, filename, lineno,
                                "Class defines hashcode(); should it be hashCode()?")
                )
        if typotoString:
            self.bug_accumulator.append(
                BugInstance('NM_LCASE_TOSTRINGE', Priorities.HIGH_PRIORITY, filename, lineno,
                           "Class defines tostring(); should it be toString()?")
            )
        if typoEquals:
            self.bug_accumulator.append(
                BugInstance('NM_LCASE_TOSTRINGE', Priorities.HIGH_PRIORITY, filename, lineno,
                            "Class defines equal(Object); should it be equals(Object)?")
            )