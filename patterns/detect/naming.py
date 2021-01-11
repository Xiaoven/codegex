import regex

from patterns.models.detectors import Detector
from patterns.models.bug_instance import BugInstance
from patterns.models import priorities

GENERIC_REGEX = regex.compile(r'(?P<gen><(?:[^<>]++|(?&gen))*>)')
CLASS_EXTENDS_REGEX = regex.compile(r'class\s+([\w$]+)\s*(?P<gen><(?:[^<>]++|(?&gen))*>)?\s+extends\s+([\w$.]+)')
INTERFACE_EXTENDS_REGEX = regex.compile(r'interface\s+([\w$]+)\s*(?P<gen><(?:[^<>]++|(?&gen))*>)?\s+extends\s+([^{]+)')


class SimpleSuperclassNameDetector(Detector):
    def __init__(self):
        # class can extend only one superclass, but implements multiple interfaces
        # extends clause must occur before implements clause
        self.pattern = CLASS_EXTENDS_REGEX
        Detector.__init__(self)

    def match(self, linecontent: str, filename: str, lineno: int, **kwargs):
        if not all(key in linecontent for key in ('class', 'extends')):
            return

        m = self.pattern.search(linecontent.strip())
        if m:
            g = m.groups()
            class_name = g[0]
            super_classes = GENERIC_REGEX.sub('', g[2])  # remove <...>
            super_classes_list = [name.rsplit('.', 1)[-1].strip() for name in super_classes.split(',')]

            if class_name in super_classes_list:
                if len(linecontent) == len(linecontent.lstrip()):
                    self.bug_accumulator.append(
                        BugInstance('NM_SAME_SIMPLE_NAME_AS_SUPERCLASS', priorities.HIGH_PRIORITY, filename, lineno,
                                    "Class names shouldn’t shadow simple name of superclass")
                    )


class SimpleInterfaceNameDetector(Detector):
    def __init__(self):
        # Check interfaces implemented by a class
        self.pattern1 = regex.compile(
            r'class\s+([\w$]+)\b.*\bimplements\s+([^{]+)')
        # Check interfaces extended by a interface
        # No implements clause allowed for interface
        # Interface can extend multiple super interfaces
        self.pattern2 = INTERFACE_EXTENDS_REGEX
        Detector.__init__(self)

    def match(self, linecontent: str, filename: str, lineno: int, **kwargs):
        if all(key in linecontent for key in ('class', 'implements')):
            m = self.pattern1.search(linecontent.strip())
        elif all(key in linecontent for key in ('interface', 'extends')):
            m = self.pattern2.search(linecontent.strip())
        else:
            return

        if m:
            g = m.groups()
            class_name = g[0]
            super_interfaces = GENERIC_REGEX.sub('', g[-1])  # remove <...>
            super_interface_list = [name.rsplit('.', 1)[-1].strip() for name in super_interfaces.split(',')]

            if class_name in super_interface_list:
                if len(linecontent) == len(linecontent.lstrip()):
                    self.bug_accumulator.append(
                        BugInstance('NM_SAME_SIMPLE_NAME_AS_INTERFACE', priorities.MEDIUM_PRIORITY, filename, lineno,
                                    "Class or interface names shouldn’t shadow simple name of implemented interface")
                    )


class HashCodeNameDetector(Detector):
    def __init__(self):
        # Check hashcode method exists
        self.pattern = regex.compile(r'^[\w\s]*?\bint\s+hashcode\s*\(\s*\)')
        Detector.__init__(self)

    def match(self, linecontent: str, filename: str, lineno: int, **kwargs):
        strip_line = linecontent.strip()
        if strip_line.startswith('private') or any(key not in linecontent for key in ('int', 'hashcode')):
            return

        m = self.pattern.match(strip_line)
        if m:
            self.bug_accumulator.append(
                BugInstance('NM_LCASE_HASHCODE', priorities.HIGH_PRIORITY, filename, lineno,
                            "Class defines hashcode(); should it be hashCode()?")
            )
