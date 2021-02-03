import regex

from patterns.models.detectors import Detector
from patterns.models.bug_instance import BugInstance
from patterns.models import priorities
from utils import log_message


class FinalizerOnExitDetector(Detector):
    def __init__(self):
        self.pattern = regex.compile(r'\b(\w+)\.runFinalizersOnExit\(')
        Detector.__init__(self)

    def match(self, context):
        line_content = context.cur_line.content
        m = self.pattern.search(line_content.strip())
        if m:
            pkg_name = m.groups()[0]
            confidence = priorities.HIGH_PRIORITY
            if pkg_name == 'System' or 'Runtime':
                confidence = priorities.MEDIUM_PRIORITY

            self.bug_accumulator.append(
                BugInstance('DM_RUN_FINALIZERS_ON_EXIT', confidence, context.cur_patch.name, context.cur_line.lineno[1],
                            'Method invokes dangerous method runFinalizersOnExit',
                            sha=context.cur_patch.sha)
            )


class RandomOnceDetector(Detector):
    def __init__(self):
        self.pattern = regex.compile(r'new\s+[\w.]*Random(?:(?P<aux1>\((?:[^()]++|(?&aux1))*\)))++\.next\w*\(\s*\)')
        Detector.__init__(self)

    def match(self, context):
        line_content = context.cur_line.content
        its = self.pattern.finditer(line_content.strip())
        for m in its:
            self.bug_accumulator.append(
                BugInstance('DMI_RANDOM_USED_ONLY_ONCE', priorities.HIGH_PRIORITY, context.cur_patch.name,
                            context.cur_line.lineno[1],
                            'Random object created and used only once',
                            sha=context.cur_patch.sha)
            )


class RandomD2IDetector(Detector):
    def __init__(self):
        self.pattern = regex.compile(r'\(\s*int\s*\)\s*(\w+)\.(?:random|nextDouble|nextFloat)\(\s*\)')
        Detector.__init__(self)

    def match(self, context):
        line_content = context.cur_line.content
        its = self.pattern.finditer(line_content.strip())
        for m in its:
            obj = m.groups()[0].strip().lower()
            if obj == 'math' or obj == 'r' or 'rand' in obj:
                self.bug_accumulator.append(
                    BugInstance('RV_01_TO_INT', priorities.HIGH_PRIORITY, context.cur_patch.name,
                                context.cur_line.lineno[1],
                                'Random value from 0 to 1 is coerced to the integer 0',
                                sha=context.cur_patch.sha)
                )


class StringCtorDetector(Detector):
    def __init__(self):
        self.pattern = regex.compile(r'new\s+String\s*(?P<aux1>\(((?:[^()]++|(?&aux1))*)\))')
        Detector.__init__(self)

    def match(self, context):
        line_content = context.cur_line.content
        its = self.pattern.finditer(line_content.strip())
        for m in its:
            groups = m.groups()
            assert len(groups) == 2

            p_type = None
            description = None

            if not groups[1] or not groups[1].strip():
                p_type = 'DM_STRING_VOID_CTOR'
                description = 'Method invokes inefficient new String() constructor'
            else:
                if groups[1].strip().startswith('"'):
                    p_type = 'DM_STRING_CTOR'
                    description = 'Method invokes inefficient new String(String) constructor'

            if p_type is not None:
                self.bug_accumulator.append(BugInstance(p_type, priorities.MEDIUM_PRIORITY, context.cur_patch.name,
                                                        context.cur_line.lineno[1],
                                                        description, sha=context.cur_patch.sha))
                return


def str_to_float(num_str: str):
    try:
        return float(num_str)
    except ValueError:
        return None


class InvalidMinMaxDetector(Detector):
    def __init__(self):
        self.pattern = regex.compile(r'Math\s*\.\s*(min|max)(?P<aux1>\(((?:[^()]++|(?&aux1))*)\))')
        self.whitespace = regex.compile(r'\s')
        Detector.__init__(self)

    def match(self, context):
        line_content = context.cur_line.content
        if not all(key in line_content for key in ('Math', 'min', 'max')):
            return

        its = self.pattern.finditer(line_content)
        for m1 in its:
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
                        self.bug_accumulator.append(BugInstance('DM_INVALID_MIN_MAX', priorities.HIGH_PRIORITY,
                                                                context.cur_patch.name, context.cur_line.lineno[1],
                                                                'Incorrect combination of Math.max and Math.min',
                                                                sha=context.cur_patch.sha))
