import regex

from codegex.models.detectors import Detector, get_exact_lineno
from codegex.models.bug_instance import BugInstance
from codegex.models.priorities import *
from codegex.utils.utils import get_string_ranges, in_range

GENERIC_REGEX = regex.compile(r'(?P<gen><(?:[^<>]++|(?&gen))*>)')
CLASS_EXTENDS_REGEX = regex.compile(r'\bclass\s+([\w$]+)\s*(?P<gen><(?:[^<>]++|(?&gen))*>)?\s+extends\s+([\w$.]+)')
INTERFACE_EXTENDS_REGEX = regex.compile(
    r'\binterface\s+([\w$]+)\s*(?P<gen><(?:[^<>]++|(?&gen))*>)?\s+extends\s+([^{]+)')
ENUM_REGEX = regex.compile(r'\benum\s+\w+\s*(?:\b(?:extends|implements)\s+[\w<>,\s]+)*\s*{')


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

        m = self.pattern.search(line_content)
        if m:
            string_ranges = get_string_ranges(line_content)
            if in_range(m.start(0), string_ranges):
                return
            g = m.groups()
            class_name = g[0]
            # A class can only have one superclass
            super_class = GENERIC_REGEX.sub('', g[2])  # remove <...>
            super_class = super_class.rsplit('.', 1)[-1].strip()

            if class_name == super_class:
                if len(line_content) == len(line_content.lstrip()):  # if do not have leading space
                    line_no = get_exact_lineno(m.end(0), context.cur_line)[1]
                    self.bug_accumulator.append(
                        BugInstance('NM_SAME_SIMPLE_NAME_AS_SUPERCLASS', HIGH_PRIORITY,
                                    context.cur_patch.name, line_no,
                                    'Class names shouldn’t shadow simple name of superclass', sha=context.cur_patch.sha,
                                    line_content=context.cur_line.content)
                    )


class SimpleInterfaceNameDetector(Detector):
    def __init__(self):
        # Check interfaces implemented by a class
        self.pattern1 = regex.compile(
            r'class\s+([\w$]+)\b.*\bimplements\s+([^{]+)', flags=regex.DOTALL)
        # Check interfaces extended by a interface
        # No implements clause allowed for interface
        # Interface can extend multiple super interfaces
        self.pattern2 = INTERFACE_EXTENDS_REGEX
        Detector.__init__(self)

    def match(self, context):
        line_content = context.cur_line.content
        if all(key in line_content for key in ('class', 'implements')):
            m = self.pattern1.search(line_content)
        elif all(key in line_content for key in ('interface', 'extends')):
            m = self.pattern2.search(line_content)
        else:
            return

        if m:
            string_ranges = get_string_ranges(line_content)
            if in_range(m.start(0), string_ranges):
                return

            g = m.groups()
            class_name = g[0]
            super_interfaces = GENERIC_REGEX.sub('', g[-1])  # remove <...>
            super_interface_list = [name.rsplit('.', 1)[-1].strip() for name in super_interfaces.split(',')]

            if class_name in super_interface_list:
                if len(line_content) == len(line_content.lstrip()):
                    line_no = get_exact_lineno(m.end(0), context.cur_line)[1]
                    self.bug_accumulator.append(
                        BugInstance('NM_SAME_SIMPLE_NAME_AS_INTERFACE', MEDIUM_PRIORITY,
                                    context.cur_patch.name, line_no,
                                    'Class or interface names shouldn’t shadow simple name of implemented interface',
                                    sha=context.cur_patch.sha, line_content=context.cur_line.content)
                    )


class HashCodeNameDetector(Detector):
    def __init__(self):
        # Check hashcode method exists
        self.pattern = regex.compile(r'\bint\s+hashcode\s*\(\s*\)')
        Detector.__init__(self)

    def match(self, context):
        line_content = context.cur_line.content
        if line_content.strip().startswith('private') or any(key not in line_content for key in ('int', 'hashcode')):
            return

        m = self.pattern.search(line_content)
        if m:
            string_ranges = get_string_ranges(line_content)
            if in_range(m.start(0), string_ranges):
                return
            line_no = get_exact_lineno(m.end(0), context.cur_line)[1]
            self.bug_accumulator.append(
                BugInstance('NM_LCASE_HASHCODE', HIGH_PRIORITY, context.cur_patch.name, line_no,
                            "Class defines hashcode(); should it be hashCode()?", sha=context.cur_patch.sha,
                            line_content=context.cur_line.content))


class ToStringNameDetector(Detector):
    def __init__(self):
        # Check hashcode method exists
        self.pattern = regex.compile(r'\bString\s+tostring\s*\(\s*\)')
        Detector.__init__(self)

    def match(self, context):
        line_content = context.cur_line.content
        if line_content.strip().startswith('private') or any(key not in line_content for key in ('String', 'tostring')):
            return
        m = self.pattern.search(line_content)
        if m:
            string_ranges = get_string_ranges(line_content)
            if in_range(m.start(0), string_ranges):
                return
            line_no = get_exact_lineno(m.end(0), context.cur_line)[1]
            self.bug_accumulator.append(
                BugInstance('NM_LCASE_TOSTRING', HIGH_PRIORITY, context.cur_patch.name, line_no,
                            'Class defines tostring(); should it be toString()?', sha=context.cur_patch.sha,
                            line_content=context.cur_line.content))


class EqualNameDetector(Detector):
    def __init__(self):
        # Check hashcode method exists
        self.pattern = regex.compile(r'\bboolean\s+equal\s*\(\s*Object\s+[\w$]+\s*\)')
        Detector.__init__(self)

    def match(self, context):
        line_content = context.cur_line.content
        if line_content.strip().startswith('private') or 'equals' in line_content \
                or any(key not in line_content for key in ('boolean', 'equal')):
            return
        m = self.pattern.search(line_content)
        if m:
            string_ranges = get_string_ranges(line_content)
            if in_range(m.start(0), string_ranges):
                return
            line_no = get_exact_lineno(m.end(0), context.cur_line)[1]
            self.bug_accumulator.append(
                BugInstance('NM_BAD_EQUAL', HIGH_PRIORITY, context.cur_patch.name, line_no,
                            'Class defines equal(Object); should it be equals(Object)?', sha=context.cur_patch.sha,
                            line_content=context.cur_line.content))


class ClassNameConventionDetector(Detector):
    def __init__(self):
        # Match class name
        self.cn_pattern = regex.compile(r'class\s+([a-z][\w$]+)[^{]*{')
        Detector.__init__(self)

    def match(self, context):
        line_content = context.cur_line.content
        if 'class ' in line_content and '{' in line_content:
            its = self.cn_pattern.finditer(line_content)
            string_ranges = get_string_ranges(line_content)
            for m in its:
                if in_range(m.start(0), string_ranges):
                    continue

                class_name = m.groups()[0]
                if "Proto$" in class_name:
                    return
                # reference from https://github.com/spotbugs/spotbugs/blob/a6f9acb2932b54f5b70ea8bc206afb552321a222
                # /spotbugs/src/main/java/edu/umd/cs/findbugs/detect/Naming.java#L389
                if '_' not in class_name:
                    priority = LOW_PRIORITY
                    if any(access in line_content for access in ('public', 'protected')):
                        priority = MEDIUM_PRIORITY

                    line_no = get_exact_lineno(m.end(0), context.cur_line)[1]
                    self.bug_accumulator.append(
                        BugInstance('NM_CLASS_NAMING_CONVENTION', priority, context.cur_patch.name, line_no,
                                    'Nm: Class names should start with an upper case letter',
                                    sha=context.cur_patch.sha, line_content=context.cur_line.content))


class MethodNameConventionDetector(Detector):
    def __init__(self):
        """
        Explanation of regex
            (\b\w+\s+)?
                for access modifiers, optional; also match "new" of "new Object()", or return type in "int Method()"
            (\b\w+(?P<gen><(?:[^<>]++|(?&gen))*>)?\s+)?
                for return type, optional; e.g. "public int" or "private Map<K, V>""
            (?:\b\w[\w.]*\.)?
                for package name chain, optional; e.g. a.b.Method()
            (\b[A-Z][a-z]\w*)\s*\(\s*
                for suspicious method name and the left parenthesis. e.g. "Method("
            (?:(?=new)|(?!new)(\w+\s+\w+)?)
                if-then conditional to extract possible "type paramName". It is one of the clues that help distinguish method definitions from method invocations.
                It equals to (?(?!new)(\w+(?&gen)?\s+\w+)?), but Python does not support conditionals using lookaround.
                
        groups:
            1 - access modifiers or "new"
            2 - return type
            3 - named captured group, e.g. "<K, V>"
            4 - method name
            5 - parameter definition, e.g. "int a"
        """
        self.mn_pattern = regex.compile(
            r'(\b\w+\s+)?(\b\w+(?P<gen><(?:[^<>]++|(?&gen))*>)?\s+)?(?:\b\w[\w.]*\.)?(\b[A-Z][a-z]\w*)\s*\(\s*(?:(?=new)|(?!new)(\w+\s+\w+)?)')
        self.patch, self.is_enum = None, False
        Detector.__init__(self)

    def match(self, context):
        line_content = context.cur_line.content
        if '(' in line_content:
            its = self.mn_pattern.finditer(line_content)
            string_ranges = get_string_ranges(line_content)
            for m in its:
                # skip if the match is a part of a string
                if in_range(m.start(0), string_ranges):
                    continue
                
                # skip annotations
                pre_str = line_content[:m.start(0)].rstrip() if m.start(0) > 0 else ''
                if pre_str and pre_str[-1] == '@':
                    continue

                # skip statements like "new Object(...)"
                modifier = m.group(1).strip() if m.group(1) else None
                if modifier == "new":
                    continue
                
                # skip constructor definitions, like "public Object(int i)"
                # Note modifier can match true modifiers, return type if modifier absent, and "new"
                is_modifier = modifier in ('public', 'private', 'protected', 'static', 'final', 'abstract',
                                           'synchronized', 'volatile')
                return_type = m.group(2)
                if is_modifier and not return_type:
                    continue
                
                # skip constructor definitions without access modifier, like "Object (int i)", "Object() {"
                # if modifier match None, it means no modifiers or return type
                param_def = m.group(5)
                is_method_def = param_def or line_content.rstrip()[-1] in ('{', '}')
                if not modifier and is_method_def:
                    continue
                
                # skip method name with "_"
                method_name = m.group(4)
                if '_' not in method_name:
                    if not is_method_def:
                        # i.e. obj.MethodName(param), or MethodName(param)
                        self._local_search(context)
                        if self.is_enum:  # skip elements defined in enum
                            continue
                        else:
                            priority = IGNORE_PRIORITY
                    else:
                        priority = LOW_PRIORITY
                        if modifier in ('public', 'protected'):
                            priority = MEDIUM_PRIORITY

                    line_no = get_exact_lineno(m.end(0), context.cur_line)[1]
                    self.bug_accumulator.append(
                        BugInstance('NM_METHOD_NAMING_CONVENTION', priority, context.cur_patch.name, line_no,
                                    'Nm: Method names should start with a lower case letter',
                                    sha=context.cur_patch.sha, line_content=context.cur_line.content))
                    return

    def _local_search(self, context):
        # check if patch is updated
        if context.cur_patch != self.patch:
            self.patch = context.cur_patch
            for hunk in self.patch:
                for line in hunk:
                    if line.prefix == '-':
                        continue
                    m = ENUM_REGEX.search(line.content)
                    if m:
                        string_ranges = get_string_ranges(line.content)
                        if not in_range(m.start(0), string_ranges):
                            self.is_enum = True
                            return
            self.is_enum = False


class ExceptionClassNameDetector(Detector):
    def __init__(self):
        # Check hashcode method exists
        self.pattern = regex.compile(r'\bclass\s+\b\w*Exception\b(?:\s+extends\s+(\w+))?')
        Detector.__init__(self)

    def match(self, context):
        line_content = context.cur_line.content
        if 'class' in line_content and 'Exception' in line_content:
            m = self.pattern.search(line_content)
            if m:
                superclassName = m.group(1)
                if not superclassName or not superclassName.endswith('Exception'):
                    string_ranges = get_string_ranges(line_content)
                    if in_range(m.start(0), string_ranges):
                        return

                    line_no = get_exact_lineno(m.end(0), context.cur_line)[1]
                    self.bug_accumulator.append(
                        BugInstance('NM_CLASS_NOT_EXCEPTION', MEDIUM_PRIORITY, context.cur_patch.name, line_no,
                                    'Class is not derived from an Exception, even though it is named as such',
                                    sha=context.cur_patch.sha, line_content=context.cur_line.content)
                    )
