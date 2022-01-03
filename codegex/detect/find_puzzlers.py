import regex

from codegex.models.priorities import *
from codegex.models.bug_instance import BugInstance
from codegex.models.detectors import Detector, get_exact_lineno
from codegex.utils.utils import convert_str_to_int, get_string_ranges, in_range, is_int_str, simple_str_to_int
from .naming import GENERIC_REGEX, INTERFACE_EXTENDS_REGEX


class BadMonthDetector(Detector):
    def __init__(self):
        self.date = regex.compile(r'\b([\w$]+)\.setMonth\s*\((\d+)\s*\)')
        self.calendar = regex.compile(r'\b([\w$]+)\.set\s*\(([^,]+,\s*(\d+)\s*[,)])')
        self.gre_calendar = regex.compile(r'new\s+GregorianCalendar\s*\([^,]+,\s*(\d+)\s*,')
        Detector.__init__(self)

    def match(self, context):
        fire = False
        instance_name = None
        month = None
        priority = MEDIUM_PRIORITY

        line_content = context.cur_line.content
        string_ranges = get_string_ranges(line_content)
        offset = None
        if 'setMonth' in line_content:
            m = self.date.search(line_content)
            if m:
                if in_range(m.start(0), string_ranges):
                    return
                offset = m.end(0)
                fire = True
                g = m.groups()
                instance_name = g[0]
                month = int(g[1])
                priority = HIGH_PRIORITY
        elif 'set' in line_content:
            if 'calendar' in line_content.lower():  # To temporarily reduce unnecessary matches
                m = self.calendar.search(line_content)
                if m:
                    if in_range(m.start(0), string_ranges):
                        return
                    offset = m.end(0)
                    g = m.groups()

                    # TODO: find object type of instance_name by local search
                    if (g[1].endswith(')') and 'Calendar.MONTH' in g[1]) or \
                            (g[1].endswith(',') and 'calendar' in g[0].lower()):
                        fire = True
                        instance_name = g[0]
                        month = int(g[2])
        elif 'GregorianCalendar' in line_content and 'new' in line_content:
            m = self.gre_calendar.search(line_content)
            if m:
                if in_range(m.start(0), string_ranges):
                    return
                offset = m.end(0)
                fire = True
                month = int(m.groups()[0])

        if fire:
            if month < 0 or month > 11:
                line_no = get_exact_lineno(offset, context.cur_line)[1]
                self.bug_accumulator.append(BugInstance('DMI_BAD_MONTH', priority, context.cur_patch.name, line_no,
                                                        'Bad constant value for month.', sha=context.cur_patch.sha,
                                                        line_content=context.cur_line.content))


class ShiftAddPriorityDetector(Detector):
    def __init__(self):
        self.pattern = regex.compile(r'\b[\w$]+\s*<<\s*([\w$]+)\s*[+-]\s*[\w$]+')
        Detector.__init__(self)

    def match(self, context):
        line_content = context.cur_line.content
        if '<<' not in line_content and '+' not in line_content:
            return

        m = self.pattern.search(line_content)
        if m:
            string_ranges = get_string_ranges(line_content)
            if in_range(m.start(0), string_ranges):
                return
            priority = LOW_PRIORITY
            const = convert_str_to_int(m.groups()[0])

            if const is not None:
                # If (foo << 32 + var) encountered for ISHL (left shift for int), then((foo << 32) + var) is absolutely
                # meaningless, but(foo << (32 + var)) can be meaningful for negative var values.
                # The same for LSHL (left shift for long)
                if const == 32 or const == 64:
                    return

                if const == 8:
                    priority = MEDIUM_PRIORITY
            line_no = get_exact_lineno(m.end(0), context.cur_line)[1]
            self.bug_accumulator.append(
                BugInstance('BSHIFT_WRONG_ADD_PRIORITY', priority, context.cur_patch.name, line_no,
                            'Possible bad parsing of shift operation.', sha=context.cur_patch.sha,
                            line_content=context.cur_line.content))


class OverwrittenIncrementDetector(Detector):
    def __init__(self):
        # 提取'='左右操作数
        self.pattern = regex.compile(
            r'(\b[\w.+$]+)\s*=([\w.\s+\-*\/]+)\s*;'
        )
        Detector.__init__(self)

    def match(self, context):
        line_content = context.cur_line.content
        if '=' in line_content and any(op in line_content for op in ('++', '--')):
            its = self.pattern.finditer(line_content)
            string_ranges = get_string_ranges(line_content)
            for m in its:
                if in_range(m.start(0), string_ranges):
                    continue
                op_1 = m.groups()[0]
                op_2 = m.groups()[1]

                # 两种可能的匹配 'a++', 'a--'
                pattern_inc = regex.compile(r'\b{}\s*\+\+|\b{}\s*--'.format(op_1, op_1))

                if pattern_inc.search(op_2):
                    line_no = get_exact_lineno(m.end(0), context.cur_line)[1]
                    self.bug_accumulator.append(
                        BugInstance('DLS_OVERWRITTEN_INCREMENT', HIGH_PRIORITY, context.cur_patch.name,
                                    line_no, "DLS: Overwritten increment", sha=context.cur_patch.sha,
                                    line_content=context.cur_line.content)
                    )
                    break


class ReuseEntryInIteratorDetector(Detector):
    def __init__(self):
        self.interface_extends = INTERFACE_EXTENDS_REGEX
        self.class_implements = regex.compile(
            r'\bclass\s+([\w$]+)\s*(?P<gen><(?:[^<>]++|(?&gen))*>)?\s+implements\s+([^{]+)')
        Detector.__init__(self)

    def match(self, context):
        line_content = context.cur_line.content
        m = None
        if all(key in line_content for key in ('class', 'implements')):
            m = self.class_implements.search(line_content)
        elif all(key in line_content for key in ('interface', 'extends')):
            m = self.interface_extends.search(line_content)

        if m:
            super_type_str = m.groups()[-1]
            super_type_str = GENERIC_REGEX.sub('', super_type_str)  # remove <...>
            super_types = [t.strip() for t in super_type_str.split(',')]
            if len(super_types) > 1 and 'Iterator' in super_types \
                    and ('Entry' in super_types or 'Map.Entry' in super_types):
                # if in string
                string_ranges = get_string_ranges(line_content)
                if in_range(m.start(0), string_ranges):
                    return
                # generate warning
                line_no = get_exact_lineno(m.end(0), context.cur_line)[1]
                self.bug_accumulator.append(
                    BugInstance('PZ_DONT_REUSE_ENTRY_OBJECTS_IN_ITERATORS', MEDIUM_PRIORITY,
                                context.cur_patch.name, line_no,
                                "shouldn't reuse Iterator as a Map.Entry",
                                sha=context.cur_patch.sha, line_content=context.cur_line.content)
                )


class MultiplyIRemResultDetector(Detector):
    def __init__(self):
        self.pattern = regex.compile(r'\b(\w+)\s*%\s*(\w+)\s*\*\s*(\w+)')
        Detector.__init__(self)

    def match(self, context):
        line_content = context.cur_line.content
        if '%' in line_content and '*' in line_content:
            itr = self.pattern.finditer(line_content)
            string_ranges = get_string_ranges(line_content)
            for m in itr:
                if m.group(1) and is_int_str(m.group(1)) or m.group(2) and is_int_str(m.group(2)) \
                        or m.group(3) and is_int_str(m.group(3)):
                    if not in_range(m.start(0), string_ranges):
                        self.bug_accumulator.append(
                            BugInstance('IM_MULTIPLYING_RESULT_OF_IREM', LOW_PRIORITY,
                                        context.cur_patch.name, get_exact_lineno(m.end(0), context.cur_line)[1],
                                        "Integer multiply of result of integer remainder",
                                        sha=context.cur_patch.sha, line_content=context.cur_line.content)
                        )


class AnonymousArrayToStringDetector(Detector):
    def __init__(self):
        self.pattern = regex.compile(
            r'\(\s*new\s+\w+\[\s*\]\s*(?P<brk>\{(?:[^{}]++|(?&brk))\})\s*\)\s*\.\s*toString\s*\(\s*\)')
        Detector.__init__(self)

    def match(self, context):
        line_content = context.cur_line.content
        if all(key in line_content for key in ('new', 'toString', '[', '{')):
            m = self.pattern.search(line_content)
            if m:
                if not in_range(m.start(0), get_string_ranges(line_content)):
                    self.bug_accumulator.append(
                        BugInstance('DMI_INVOKING_TOSTRING_ON_ANONYMOUS_ARRAY', MEDIUM_PRIORITY,
                                    context.cur_patch.name, get_exact_lineno(m.end(0), context.cur_line)[1],
                                    "Invocation of toString on an unnamed array",
                                    sha=context.cur_patch.sha, line_content=context.cur_line.content)
                    )


class BoxingImmediatelyUnboxedDetector(Detector):
    def __init__(self):
        self.pattern = regex.compile(r'\bnew\s+(Byte|Short|Integer|Long|Float|Double|Character|Boolean)\s*\(.+\)\.(\w+)'
                                     r'Value\s*\(\s*\)')
        self.pattern_ctor = regex.compile(r'\bnew\s+(Integer|Long|Short|Byte|Double|Float)\s*(?P<aux1>\(((?:[^()]++|(?&aux1))*)\))')
        Detector.__init__(self)

    def match(self, context):
        line_content = context.cur_line.content
        if 'new' not in line_content and \
                not any(key in line_content for key in ('Byte', 'Short', 'Integer', 'Long',
                                                        'Float', 'Double', 'Character', 'Boolean')):
            return
        m = self.pattern.search(line_content)
        if m:
            prev_class = m.groups()[0]
            this_method = m.groups()[1]
            if prev_class.lower() == this_method:
                self.bug_accumulator.append(
                    BugInstance('BX_BOXING_IMMEDIATELY_UNBOXED', MEDIUM_PRIORITY,
                                context.cur_patch.name, get_exact_lineno(m.end(0), context.cur_line)[1],
                                "Primitive value is boxed and then immediately unboxed",
                                sha=context.cur_patch.sha, line_content=context.cur_line.content)
                )
            else:
                self.bug_accumulator.append(
                    BugInstance('BX_BOXING_IMMEDIATELY_UNBOXED_TO_PERFORM_COERCION', MEDIUM_PRIORITY,
                                context.cur_patch.name, get_exact_lineno(m.end(0), context.cur_line)[1],
                                "Primitive value is boxed then unboxed to perform primitive coercion",
                                sha=context.cur_patch.sha, line_content=context.cur_line.content)
                )
        else:
            m = self.pattern_ctor.search(line_content)
            if m and not in_range(m.start(0), get_string_ranges(line_content)):
                if m.group(1) not in ('Double', 'Float'):
                    int_val = simple_str_to_int(m.group(3).strip('"'))
                    priority = MEDIUM_PRIORITY
                    if int_val is not None and (int_val > -128 or int_val > 127):
                        priority = LOW_PRIORITY

                    self.bug_accumulator.append(
                        BugInstance('DM_NUMBER_CTOR', priority, context.cur_patch.name,
                                    get_exact_lineno(m.end(0), context.cur_line)[1],
                                    'Method invokes inefficient Number constructor; use static valueOf instead',
                                    sha=context.cur_patch.sha, line_content=context.cur_line.content)
                    )
                else:
                    self.bug_accumulator.append(
                        BugInstance(
                            'DM_FP_NUMBER_CTOR', LOW_PRIORITY, context.cur_patch.name,
                            get_exact_lineno(m.end(0), context.cur_line)[1],
                            'Method invokes inefficient floating-point Number constructor; use static valueOf instead',
                            sha=context.cur_patch.sha, line_content=context.cur_line.content)
                    )

