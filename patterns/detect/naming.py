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

    def match(self, context):
        line_content = context.cur_line.content
        if not all(key in line_content for key in ('class', 'extends')):
            return

        m = self.pattern.search(line_content.strip())
        if m:
            g = m.groups()
            class_name = g[0]
            super_classes = GENERIC_REGEX.sub('', g[2])  # remove <...>
            super_classes_list = [name.rsplit('.', 1)[-1].strip() for name in super_classes.split(',')]

            if class_name in super_classes_list:
                if len(line_content) == len(line_content.lstrip()):
                    self.bug_accumulator.append(
                        BugInstance('NM_SAME_SIMPLE_NAME_AS_SUPERCLASS', priorities.HIGH_PRIORITY,
                                    context.cur_patch.name, context.cur_line.lineno[1],
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

    def match(self, context):
        line_content = context.cur_line.content
        if all(key in line_content for key in ('class', 'implements')):
            m = self.pattern1.search(line_content.strip())
        elif all(key in line_content for key in ('interface', 'extends')):
            m = self.pattern2.search(line_content.strip())
        else:
            return

        if m:
            g = m.groups()
            class_name = g[0]
            super_interfaces = GENERIC_REGEX.sub('', g[-1])  # remove <...>
            super_interface_list = [name.rsplit('.', 1)[-1].strip() for name in super_interfaces.split(',')]

            if class_name in super_interface_list:
                if len(line_content) == len(line_content.lstrip()):
                    self.bug_accumulator.append(
                        BugInstance('NM_SAME_SIMPLE_NAME_AS_INTERFACE', priorities.MEDIUM_PRIORITY,
                                    context.cur_patch.name, context.cur_line.lineno[1],
                                    "Class or interface names shouldn’t shadow simple name of implemented interface")
                    )


class HashCodeNameDetector(Detector):
    def __init__(self):
        # Check hashcode method exists
        self.pattern = regex.compile(r'^[\w\s]*?\bint\s+hashcode\s*\(\s*\)')
        Detector.__init__(self)

    def match(self, context):
        line_content = context.cur_line.content
        strip_line = line_content.strip()
        if strip_line.startswith('private') or any(key not in line_content for key in ('int', 'hashcode')):
            return

        m = self.pattern.match(strip_line)
        if m:
            self.bug_accumulator.append(BugInstance('NM_LCASE_HASHCODE', priorities.HIGH_PRIORITY,
                                                    context.cur_patch.name, context.cur_line.lineno[1],
                                                    "Class defines hashcode(); should it be hashCode()?"))


class ToStringNameDetector(Detector):
    def __init__(self):
        # Check hashcode method exists
        self.pattern = regex.compile(r'^[\w\s]*?\bString\s+tostring\s*\(\s*\)')
        Detector.__init__(self)

    def match(self, context):
        line_content = context.cur_line.content
        strip_line = line_content.strip()
        if strip_line.startswith('private') or any(key not in line_content for key in ('String', 'tostring')):
            return
        m = self.pattern.search(strip_line)
        if m:
            self.bug_accumulator.append(
                BugInstance('NM_LCASE_TOSTRING', priorities.HIGH_PRIORITY, context.cur_patch.name,
                            context.cur_line.lineno[1],
                            "Class defines tostring(); should it be toString()?"))


class EqualNameDetector(Detector):
    def __init__(self):
        # Check hashcode method exists
        self.pattern = regex.compile(r'^[\w\s]*?\bboolean\s+equal\s*\(\s*Object\s+[\w$]+\s*\)')
        Detector.__init__(self)

    def match(self, context):
        line_content = context.cur_line.content
        strip_line = line_content.strip()
        if strip_line.startswith('private') or 'equals' in line_content \
                or any(key not in line_content for key in ('boolean', 'equal')):
            return
        m = self.pattern.search(strip_line)
        if m:
            self.bug_accumulator.append(BugInstance('NM_BAD_EQUAL', priorities.HIGH_PRIORITY, context.cur_patch.name,
                                                    context.cur_line.lineno[1],
                                                    "Class defines equal(Object); should it be equals(Object)?"))
