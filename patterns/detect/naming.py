import regex

from patterns.models.detectors import Detector
from patterns.models.bug_instance import BugInstance
from patterns.models import priorities
from utils import get_string_ranges, in_range

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
                                    'Class names shouldn’t shadow simple name of superclass', sha=context.cur_patch.sha)
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
                                    'Class or interface names shouldn’t shadow simple name of implemented interface',
                                    sha=context.cur_patch.sha)
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
                                                    "Class defines hashcode(); should it be hashCode()?",
                                                    sha=context.cur_patch.sha))


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
                            'Class defines tostring(); should it be toString()?', sha=context.cur_patch.sha))


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
                                                    'Class defines equal(Object); should it be equals(Object)?',
                                                    sha=context.cur_patch.sha))


class ClassNameConventionDetector(Detector):
    def __init__(self):
        # Match class name
        self.cn_pattern = regex.compile(r'class\s+([a-z][\w$]+).*{')
        Detector.__init__(self)

    def match(self, context):
        strip_line = context.cur_line.content.strip()
        if 'class ' in strip_line and '{' in strip_line:
            its = self.cn_pattern.finditer(strip_line)
            for m in its:
                class_name = m.groups()[0]
                if "Proto$" in class_name:
                    return
                # reference from https://github.com/spotbugs/spotbugs/blob/a6f9acb2932b54f5b70ea8bc206afb552321a222
                # /spotbugs/src/main/java/edu/umd/cs/findbugs/detect/Naming.java#L389
                if '_' not in class_name:
                    priority = priorities.LOW_PRIORITY
                    if any(access in strip_line for access in ('public', 'protected')):
                        priority = priorities.MEDIUM_PRIORITY

                    self.bug_accumulator.append(
                        BugInstance('NM_CLASS_NAMING_CONVENTION', priority, context.cur_patch.name,
                                    context.cur_line.lineno[1],
                                    'Nm: Class names should start with an upper case letter',
                                    sha=context.cur_patch.sha))


class MethodNameConventionDetector(Detector):
    def __init__(self):
        # Extract the method name
        self.mn_pattern = regex.compile(
            r'(\b\w+\s+)?(?:\b\w+\s*\.\s*)*(\b\w+)\s*\(\s*((?:(?!new)\w)+(?P<gen><(?:[^<>]++|(?&gen))*>)?\s+\w+)?')
        Detector.__init__(self)

    def match(self, context):
        strip_line = context.cur_line.content.strip()
        if '(' in strip_line:
            its = self.mn_pattern.finditer(strip_line)
            for m in its:
                g = m.groups()
                pre_token = g[0].strip() if g[0] else g[0]
                method_name = g[1]
                args_def = g[2]

                # skip statements like "new Object(...)"
                if pre_token == 'new':
                    continue
                # skip constructor definitions, like "public Object(int i)"
                if pre_token in ('public', 'private', 'protected', 'static'):
                    continue
                # skip constructor definitions without access modifier, like "Object (int i)", "Object() {"
                if not pre_token and (args_def or strip_line.endswith('{')):
                    continue
                # skip match within string
                string_ranges = get_string_ranges(strip_line)
                method_name_offset = m.start(2)
                if in_range(method_name_offset, string_ranges):
                    continue
                # skip annotations
                if method_name_offset - 1 >= 0 and strip_line[method_name_offset - 1] == '@':
                    continue

                if len(method_name) >= 2 and method_name[0].isalpha() and not method_name[0].islower() and \
                        method_name[1].isalpha() and method_name[1].islower() and '_' not in method_name:
                    priority = priorities.LOW_PRIORITY
                    if any(access in strip_line for access in ('public', 'protected')):
                        priority = priorities.MEDIUM_PRIORITY

                    self.bug_accumulator.append(
                        BugInstance('NM_METHOD_NAMING_CONVENTION', priority, context.cur_patch.name,
                                    context.cur_line.lineno[1],
                                    'Nm: Method names should start with a lower case letter',
                                    sha=context.cur_patch.sha))
                    return
