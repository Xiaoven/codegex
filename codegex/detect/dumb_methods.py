import regex
from decimal import Decimal

from codegex.models.priorities import *
from codegex.models.bug_instance import BugInstance
from codegex.models.detectors import Detector, get_exact_lineno
from codegex.utils.utils import log_message, get_string_ranges, in_range, str_to_float, simple_str_to_int


class FinalizerOnExitDetector(Detector):
    def __init__(self):
        self.pattern = regex.compile(r'\b(\w+)\s*\.\s*runFinalizersOnExit\s*\(')
        Detector.__init__(self)

    def match(self, context):
        line_content = context.cur_line.content
        m = self.pattern.search(line_content)
        if m:
            string_ranges = get_string_ranges(line_content)
            if in_range(m.start(0), string_ranges):
                return

            pkg_name = m.groups()[0]
            confidence = HIGH_PRIORITY
            if pkg_name == 'System' or 'Runtime':
                confidence = MEDIUM_PRIORITY

            line_no = get_exact_lineno(m.end(0), context.cur_line)[1]
            self.bug_accumulator.append(
                BugInstance('DM_RUN_FINALIZERS_ON_EXIT', confidence, context.cur_patch.name, line_no,
                            'Method invokes dangerous method runFinalizersOnExit', sha=context.cur_patch.sha, line_content=context.cur_line.content)
            )


class RandomOnceDetector(Detector):
    def __init__(self):
        self.pattern = regex.compile(
            r'\bnew\s+[\w.]*Random(?P<aux1>\((?:[^()]++|(?&aux1))*\))++\s*\.\s*next(?:Boolean|Bytes|Double|Float|Gaussian|Int|Long)\([^),]*\)')
        Detector.__init__(self)

    def match(self, context):
        line_content = context.cur_line.content
        its = self.pattern.finditer(line_content)
        string_ranges = get_string_ranges(line_content)
        for m in its:
            if in_range(m.start(0), string_ranges):
                continue

            # m.start(1) is the offset of the naming group
            line_no = get_exact_lineno(m.start(1), context.cur_line)[1]
            self.bug_accumulator.append(
                BugInstance('DMI_RANDOM_USED_ONLY_ONCE', HIGH_PRIORITY, context.cur_patch.name, line_no,
                            'Random object created and used only once', sha=context.cur_patch.sha, line_content=context.cur_line.content)
            )
            return


class RandomD2IDetector(Detector):
    def __init__(self):
        self.pattern = regex.compile(r'\(\s*int\s*\)\s*\b(\w+)\s*\.\s*(random|nextDouble|nextFloat)\s*\(\s*\)')
        Detector.__init__(self)

    def match(self, context):
        line_content = context.cur_line.content
        its = self.pattern.finditer(line_content)
        string_ranges = get_string_ranges(line_content)
        for m in its:
            if in_range(m.start(0), string_ranges):
                continue
            obj = m.group(1).strip().lower()
            if obj == 'math' or obj == 'r' or 'rand' in obj:
                line_no = get_exact_lineno(m.end(2), context.cur_line)[1]
                self.bug_accumulator.append(
                    BugInstance('RV_01_TO_INT', HIGH_PRIORITY, context.cur_patch.name, line_no,
                                'Random value from 0 to 1 is coerced to the integer 0', sha=context.cur_patch.sha, line_content=context.cur_line.content)
                )
                return


class StringCtorDetector(Detector):
    def __init__(self):
        self.pattern = regex.compile(r'\bnew\s+String\s*(?P<aux1>\(((?:[^()]++|(?&aux1))*)\))')
        self.pattern_space = regex.compile(r'\s')
        Detector.__init__(self)

    def match(self, context):
        line_content = context.cur_line.content
        its = self.pattern.finditer(line_content)
        string_ranges = get_string_ranges(line_content)
        for m in its:
            start_offset = m.start(0)
            if in_range(start_offset, string_ranges):
                continue

            groups = m.groups()
            assert len(groups) == 2

            p_type = None
            description = None

            target = self.pattern_space.sub('', groups[1])
            if not target:
                p_type = 'DM_STRING_VOID_CTOR'
                description = 'Method invokes inefficient new String() constructor'
            else:
                if target.startswith('"') or '.substring(' in target:
                    p_type = 'DM_STRING_CTOR'
                    description = 'Method invokes inefficient new String(String) constructor'

            if p_type is not None:
                # m.start(1) is the offset of the naming group
                line_no = get_exact_lineno(m.start(1), context.cur_line)[1]
                self.bug_accumulator.append(BugInstance(p_type, MEDIUM_PRIORITY, context.cur_patch.name,
                                                        line_no, description, sha=context.cur_patch.sha, line_content=context.cur_line.content))
                return


class InvalidMinMaxDetector(Detector):
    def __init__(self):
        self.pattern = regex.compile(r'\bMath\s*\.\s*(min|max)\s*(?P<aux1>\(((?:[^()]++|(?&aux1))*)\))')
        self.whitespace = regex.compile(r'\s')
        Detector.__init__(self)

    def match(self, context):
        line_content = context.cur_line.content
        if not all(key in line_content for key in ('Math', 'min', 'max')):
            return

        its = self.pattern.finditer(line_content)
        string_ranges = get_string_ranges(line_content)
        for m1 in its:
            start_offset = m1.start(0)
            if in_range(start_offset, string_ranges):
                continue

            g1 = m1.groups()
            outer_method = g1[0]
            arg_str_1 = self.whitespace.sub('', g1[-1])

            m2 = self.pattern.search(arg_str_1)
            if m2:
                g2 = m2.groups()
                inner_method = g2[0]
                arg_str_2 = g2[-1]

                if any(method not in (outer_method, inner_method) for method in ('min', 'max')):
                    return

                if m2.start() == 0:
                    const_1 = str_to_float(arg_str_1[m2.end() + 1:])
                else:
                    const_1 = str_to_float(arg_str_1[:m2.start() - 1])

                inner_args = arg_str_2.split(',')
                if len(inner_args) != 2:
                    log_message(f'[InvalidMinMaxDetector] More than one commas for {line_content}', 'error')
                    return

                const_2 = None
                for arg in inner_args:
                    const_2 = str_to_float(arg)
                    if const_2 is not None:
                        break

                if all(const is not None for const in (const_1, const_2)):
                    if outer_method == 'min':  # Math.min(const_1, Math.max(const_2, variable))
                        upper_bound = const_1
                        lower_bound = const_2
                    else:  # Math.max(const_1, Math.min(const_2, variable))
                        upper_bound = const_2
                        lower_bound = const_1

                    if upper_bound < lower_bound:
                        line_no = get_exact_lineno(m1.end(0), context.cur_line)[1]
                        self.bug_accumulator.append(
                            BugInstance('DM_INVALID_MIN_MAX', HIGH_PRIORITY, context.cur_patch.name, line_no,
                                        'Incorrect combination of Math.max and Math.min', sha=context.cur_patch.sha, line_content=context.cur_line.content))


class VacuousEasyMockCallDetector(Detector):
    def __init__(self):
        self.pattern = regex.compile(r'\bEasyMock\.(?:verify|replay|(?:reset\w*))\s*\(\s*\)')
        Detector.__init__(self)

    def match(self, context):
        line_content = context.cur_line.content
        if 'EasyMock' in line_content and any(key in line_content for key in ('verify', 'replay', 'reset')):
            m = self.pattern.search(line_content)
            if m:
                string_ranges = get_string_ranges(line_content)
                if in_range(m.start(0), string_ranges):
                    return

                self.bug_accumulator.append(
                    BugInstance('DMI_VACUOUS_CALL_TO_EASYMOCK_METHOD', HIGH_PRIORITY, context.cur_patch.name,
                                get_exact_lineno(m.end(0), context.cur_line)[1],
                                'Useless/vacuous call to EasyMock method',
                                sha=context.cur_patch.sha, line_content=context.cur_line.content)
                )


class BigDecimalConstructorDetector(Detector):
    def __init__(self):
        self.pattern = regex.compile(r'\bnew\s+BigDecimal\s*\(\s*(\d+\.\d+)\s*\)')
        Detector.__init__(self)

    def match(self, context):
        line_content = context.cur_line.content
        if all(key in line_content for key in ('new', 'BigDecimal', '.')):
            itr = self.pattern.finditer(line_content)
            string_ranges = get_string_ranges(line_content)
            for m in itr:
                if in_range(m.start(0), string_ranges):
                    continue
                value = float(m.group(1))
                floatStr = str(value)  # trim useless 0
                decimalValue = Decimal(value)
                decimalValueStr = str(decimalValue)

                if floatStr != decimalValueStr and floatStr != decimalValueStr + '.0':
                    priority = MEDIUM_PRIORITY if len(floatStr) <= 8 and len(decimalValueStr) > 12 \
                                                  and 'E' not in decimalValueStr else LOW_PRIORITY

                    self.bug_accumulator.append(
                        BugInstance('DMI_BIGDECIMAL_CONSTRUCTED_FROM_DOUBLE', priority, context.cur_patch.name,
                                    get_exact_lineno(m.end(0), context.cur_line)[1],
                                    'BigDecimal constructed from double that isn’t represented precisely',
                                    sha=context.cur_patch.sha, line_content=context.cur_line.content)
                    )


class NonsensicalInvocationDetector(Detector):
    def __init__(self):
        self.pattern = regex.compile(
            r'\b(?:Preconditions\.checkNotNull|Strings\.(?:nullToEmpty|emptyToNull|isNullOrEmpty))\s*\(\s*(?P<str>"[^"]*")\s*(?:,\s*(\w+|(?&str)))?')
        self.pattern2 = regex.compile(r'Assert\.assertNotNull\s*\(\s*(\w+,\s*)?"[^"]+"\s*\)')
        Detector.__init__(self)

    def match(self, context):
        line_content = context.cur_line.content
        if any(clazzName in line_content for clazzName in ('Preconditions', 'Strings')) and \
                any(methodName in line_content for methodName in ('checkNotNull', 'nullToEmpty', 'emptyToNull', 'isNullOrEmpty')):
            itr = self.pattern.finditer(line_content)
            string_ranges = get_string_ranges(line_content)
            for m in itr:
                if in_range(m.start(0), string_ranges):
                    continue
                patternName = 'DMI_DOH'
                description = 'D’oh! A nonsensical method invocation'

                secondParam = m.group(2)
                if secondParam is not None and not secondParam.startswith('"'):
                    patternName = 'DMI_ARGUMENTS_WRONG_ORDER'
                    description = 'Reversed method arguments'

                self.bug_accumulator.append(
                    BugInstance(patternName, MEDIUM_PRIORITY, context.cur_patch.name,
                                get_exact_lineno(m.end(0), context.cur_line)[1],
                                description, sha=context.cur_patch.sha, line_content=context.cur_line.content)
                )

        if all(key in line_content for key in ('Assert', 'assertNotNull')):
            itr = self.pattern2.finditer(line_content)
            string_ranges = get_string_ranges(line_content)
            for m in itr:
                if in_range(m.start(0), string_ranges):
                    return

                patternName = 'DMI_DOH'
                description = 'D’oh! A nonsensical method invocation'

                if m.group(1) is not None:
                    patternName = 'DMI_ARGUMENTS_WRONG_ORDER'
                    description = 'Reversed method arguments'

                self.bug_accumulator.append(
                    BugInstance(patternName, MEDIUM_PRIORITY, context.cur_patch.name,
                                get_exact_lineno(m.end(0), context.cur_line)[1],
                                description, sha=context.cur_patch.sha, line_content=context.cur_line.content)
                )


class BooleanCtorDetector(Detector):
    def __init__(self):
        self.pattern = regex.compile(r'\bnew\s+Boolean\s*(?P<aux1>\(((?:[^()]++|(?&aux1))*)\))')
        Detector.__init__(self)

    def match(self, context):
        line_content = context.cur_line.content
        if all(key in line_content for key in ('new', 'Boolean')):
            m = self.pattern.search(line_content)
            if m and not in_range(m.start(0), get_string_ranges(line_content)):
                self.bug_accumulator.append(
                    BugInstance('DM_BOOLEAN_CTOR', MEDIUM_PRIORITY, context.cur_patch.name,
                                get_exact_lineno(m.end(0), context.cur_line)[1],
                                'Method invokes inefficient Boolean constructor; use Boolean.valueOf(…) instead',
                                sha=context.cur_patch.sha, line_content=context.cur_line.content)
                )


class BoxedPrimitiveToStringDetector(Detector):
    def __init__(self):
        Detector.__init__(self)
        self.pattern_1 = regex.compile(
            r'\bnew\s+(?:Integer|Long|Float|Double|Byte|Short|Boolean)\s*\(\s*(?:[\d.]+|true|false)\s*\)\s*\.\s*toString\s*\(\s*\)')
        self.pattern_2 = regex.compile(
            r'\bInteger\s*\.\s*valueOf\s*\(\s*\d+\s*\)\s*\.\s*toString\s*\(\s*\)')

    def match(self, context):
        line_content = context.cur_line.content
        m = None
        priority = MEDIUM_PRIORITY
        if all(k in line_content for k in ('new', 'toString')) and any(
                k in line_content for k in ('Integer', 'Long', 'Float', 'Double', 'Byte', 'Short', 'Boolean')):
            m = self.pattern_1.search(line_content)
        elif all(k in line_content for k in ('Integer', 'valueOf', 'toString')):
            m = self.pattern_2.search(line_content)
            priority = HIGH_PRIORITY

        if m and not in_range(m.start(0), get_string_ranges(line_content)):
            self.bug_accumulator.append(
                BugInstance(
                    'DM_BOXED_PRIMITIVE_TOSTRING', priority, context.cur_patch.name,
                    get_exact_lineno(m.end(0), context.cur_line)[1],
                    'Method invokes inefficient floating-point Number constructor; use static valueOf instead',
                    sha=context.cur_patch.sha, line_content=context.cur_line.content)
            )


class BoxedPrimitiveForParsingDetector(Detector):
    def __init__(self):
        Detector.__init__(self)
        self.pattern_1 = regex.compile(
            r'\(?\bnew\s+(?:Integer|Long|Double|Float)\s*\(\s*["\w]+\s*\)\s*\)?\s*\.\s*(?:int|long|double|float)Value\s*\(\s*\)')
        self.pattern_2 = regex.compile(
            r'\b(?:Integer|Long|Double|Float)\s*\.\s*valueOf\s*\(\s*["\w]+\s*\)\s*\.\s*(?:int|long|double|float)Value\s*\(\s*\)')

    def match(self, context):
        line_content = context.cur_line.content
        m = None
        if any(k in line_content for k in ('Integer', 'Long', 'Float', 'Double')) \
                and any(k in line_content for k in ('intValue', 'longValue', 'floatValue', 'doubleValue')):
            if 'new' in line_content:
                m = self.pattern_1.search(line_content)
            elif 'valueOf' in line_content:
                m = self.pattern_2.search(line_content)

            if m and not in_range(m.start(0), get_string_ranges(line_content)):
                self.bug_accumulator.append(
                    BugInstance(
                        'DM_BOXED_PRIMITIVE_FOR_PARSING', HIGH_PRIORITY, context.cur_patch.name,
                        get_exact_lineno(m.end(0), context.cur_line)[1],
                        'Boxing/unboxing to parse a primitive',
                        sha=context.cur_patch.sha, line_content=context.cur_line.content)
                )


class BoxedPrimitiveForCompareDetector(Detector):
    def __init__(self):
        Detector.__init__(self)
        self.pattern = regex.compile(
            r'\(\s*\(\s*(?:Long|Integer)\s*\)\s*\w(?:[.\w]+|(?P<aux>\((?:[^()]++|(?&aux))*\)))*\s*\)\s*\.compareTo\s*(?&aux)')

    def match(self, context):
        line_content = context.cur_line.content
        if 'compareTo' in line_content and any(k for k in ('Integer', 'Long')):
            m = self.pattern.search(line_content)
            if m and not in_range(m.start(0), get_string_ranges(line_content)):
                self.bug_accumulator.append(
                    BugInstance(
                        'DM_BOXED_PRIMITIVE_FOR_COMPARE', LOW_PRIORITY, context.cur_patch.name,
                        get_exact_lineno(m.end(0), context.cur_line)[1],
                        'Boxing/unboxing to parse a primitive',
                        sha=context.cur_patch.sha, line_content=context.cur_line.content)
                )
                

class NewForGetclassDetector(Detector):
    def __init__(self):
        Detector.__init__(self)
        self.pattern = regex.compile(
            r'\(?\bnew\s+[\w.]+\s*(?P<aux1>\((?:[^()]++|(?&aux1))*\))\s*\)?\s*\.\s*getClass\s*\(\s*\)')

    def match(self, context):
        line_content = context.cur_line.content
        if 'new' not in line_content:
            return
        m = self.pattern.search(line_content)
        if m and not in_range(m.start(0), get_string_ranges(line_content)):
            line_no = get_exact_lineno(m.end(0), context.cur_line)[1]
            self.bug_accumulator.append(
                BugInstance(
                    'DM_NEW_FOR_GETCLASS', MEDIUM_PRIORITY, context.cur_patch.name, line_no,
                    'Method allocates an object, only to get the class object',
                    sha=context.cur_patch.sha,
                    line_content=context.cur_line.content)
            )


class NextIntViaNextDoubleDetector(Detector):
    def __init__(self):
        Detector.__init__(self)
        self.pattern = regex.compile(
            r'\(\s*int\s*\)\s*\(\s*(?P<op>(\w+\s*\.\s*(?:random|nextDouble|nextFloat)\s*\(\s*\))|\w[\w.]*)\s*\*\s*((?&op))\s*\)')
        self.random_pattern = regex.compile(r'^\w+\s*\.\s*(?:random|nextDouble|nextFloat)\s*\(\s*\)$')

    def match(self, context):
        line_content = context.cur_line.content
        if 'int' not in line_content or not any(key in line_content for key in ('random', 'nextFloat', 'nextDouble')):
            return
        itr = self.pattern.finditer(line_content)
        str_range = get_string_ranges(line_content)
        for m in itr:
            if not in_range(m.start(0), str_range):
                target = m.group(2)
                if not target and self.random_pattern.match(m.group(3)):  # 第一个乘数不是random invocation，检查第二个乘数
                    target = m.group(3)

                if target:
                    if target.endswith('random') and not target.startswith('Math'):  # 检查 Math.random()
                        continue
                    line_no = get_exact_lineno(m.end(0), context.cur_line)[1]
                    self.bug_accumulator.append(
                        BugInstance('DM_NEXTINT_VIA_NEXTDOUBLE', MEDIUM_PRIORITY, context.cur_patch.name, line_no,
                                    'Use the nextInt method of Random rather than nextDouble to generate a random integer.',
                                    sha=context.cur_patch.sha,
                                    line_content=context.cur_line.content)
                    )
                    break   # 一行报一个 warning 就够了


class ImmediateDereferenceOfReadlineDetector(Detector):
    def __init__(self):
        Detector.__init__(self)
        self.pattern = regex.compile(r'\b\.readLine\s*\(\s*\)\s*\.')

    def match(self, context):
        line_content = context.cur_line.content
        if 'readLine' not in line_content:
            return
        m = self.pattern.search(line_content)
        if m:
            line_no = get_exact_lineno(m.end(0), context.cur_line)[1]
            self.bug_accumulator.append(
                BugInstance('NP_IMMEDIATE_DEREFERENCE_OF_READLINE', MEDIUM_PRIORITY, context.cur_patch.name, line_no,
                            'Immediate dereference of the result of readLine()',
                            sha=context.cur_patch.sha,
                            line_content=context.cur_line.content)
            )