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
            self.bug_accumulator.append(BugInstance('NM_LCASE_HASHCODE', priorities.HIGH_PRIORITY, filename, lineno,
                                                    "Class defines hashcode(); should it be hashCode()?"))


class ToStringNameDetector(Detector):
    def __init__(self):
        # Check hashcode method exists
        self.pattern = regex.compile(r'^[\w\s]*?\bString\s+tostring\s*\(\s*\)')
        Detector.__init__(self)

    def match(self, linecontent: str, filename: str, lineno: int, **kwargs):
        strip_line = linecontent.strip()
        if strip_line.startswith('private') or any(key not in linecontent for key in ('String', 'tostring')):
            return
        m = self.pattern.search(strip_line)
        if m:
            self.bug_accumulator.append(BugInstance('NM_LCASE_TOSTRING', priorities.HIGH_PRIORITY, filename, lineno,
                                                    "Class defines tostring(); should it be toString()?"))


class EqualNameDetector(Detector):
    def __init__(self):
        # Check hashcode method exists
        self.pattern = regex.compile(r'^[\w\s]*?\bboolean\s+equal\s*\(\s*Object\s+[\w$]+\s*\)')
        Detector.__init__(self)

    def match(self, linecontent: str, filename: str, lineno: int, **kwargs):
        strip_line = linecontent.strip()
        if strip_line.startswith('private') or 'equals' in linecontent \
                or any(key not in linecontent for key in ('boolean', 'equal')):
            return
        m = self.pattern.search(strip_line)
        if m:
            self.bug_accumulator.append(BugInstance('NM_BAD_EQUAL', priorities.HIGH_PRIORITY, filename, lineno,
                                                    "Class defines equal(Object); should it be equals(Object)?"))


class ClassNameConventionDetector(Detector):
    def __init__(self):
        # Match class name
        self.cn_pattern = regex.compile(r'class\s+([a-z][\w$]+).*{')
        Detector.__init__(self)

    def match(self, linecontent: str, filename: str, lineno: int, **kwargs):
        strip_line = linecontent.strip()
        if 'class ' in strip_line and '{' in strip_line:
            its = self.cn_pattern.finditer(strip_line)
            for m in its:
                class_name = m.groups()[0]
                if "Proto$" in class_name:
                    return
                # reference from https://github.com/spotbugs/spotbugs/blob/a6f9acb2932b54f5b70ea8bc206afb552321a222
                # /spotbugs/src/main/java/edu/umd/cs/findbugs/detect/Naming.java#L389
                if '_' not in class_name:
                    if any(access in strip_line for access in ('public', 'protected')):
                        self.bug_accumulator.append(BugInstance('NM_CLASS_NAMING_CONVENTION',
                                                                priorities.MEDIUM_PRIORITY, filename, lineno,
                                                                "Nm: Class names should start with an upper case letter"))
                    else:
                        self.bug_accumulator.append(BugInstance('NM_CLASS_NAMING_CONVENTION',
                                                                priorities.LOW_PRIORITY, filename, lineno,
                                                                "Nm: Class names should start with an upper case letter"))


class MethodNameConventionDetector(Detector):
    def __init__(self):
        # Extract the method name
        self.mn_pattern = regex.compile(r'\b\w+[\s.]+(\w+)\s*\(')
        Detector.__init__(self)

    def match(self, linecontent: str, filename: str, lineno: int, **kwargs):
        strip_line = linecontent.strip()
        if '(' in strip_line and ')' in strip_line:
            its = self.mn_pattern.finditer(strip_line)
            for m in its:
                method_name = m.groups()[0]
                if len(method_name) >= 2 and method_name[0].isalpha() and not method_name[0].islower() and \
                        method_name[1].isalpha() and method_name[1].islower() and '_' not in method_name:
                    if any(access in strip_line for access in ('public', 'protected')):
                        self.bug_accumulator.append(BugInstance('NM_METHOD_NAMING_CONVENTION', priorities.MEDIUM_PRIORITY, filename, lineno,
                                                                "Nm: Method names should start with a lower case letter"))
                    else:
                        self.bug_accumulator.append(
                            BugInstance('NM_METHOD_NAMING_CONVENTION', priorities.LOW_PRIORITY, filename, lineno,
                                        "Nm: Method names should start with a lower case letter"))
