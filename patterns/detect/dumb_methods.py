import regex

from patterns.models.detectors import Detector
from patterns.models.bug_instance import BugInstance
from patterns.models import priorities
from utils import log_message


class FinalizerOnExitDetector(Detector):
    def __init__(self):
        self.pattern = regex.compile(r'\b(\w+)\.runFinalizersOnExit\(')
        Detector.__init__(self)

    def match(self, linecontent: str, filename: str, lineno: int, **kwargs):
        m = self.pattern.search(linecontent.strip())
        if m:
            pkg_name = m.groups()[0]
            confidence = priorities.HIGH_PRIORITY
            if pkg_name == 'System' or 'Runtime':
                confidence = priorities.MEDIUM_PRIORITY

            self.bug_accumulator.append(
                BugInstance('DM_RUN_FINALIZERS_ON_EXIT', confidence, filename, lineno,
                            'Method invokes dangerous method runFinalizersOnExit')
            )


class RandomOnceDetector(Detector):
    def __init__(self):
        self.pattern = regex.compile(r'new\s+[\w.]*Random(?:(?P<aux1>\((?:[^()]++|(?&aux1))*\)))++\.next\w*\(\s*\)')
        Detector.__init__(self)

    def match(self, linecontent: str, filename: str, lineno: int, **kwargs):
        m = self.pattern.search(linecontent.strip())
        if m:
            self.bug_accumulator.append(
                BugInstance('DMI_RANDOM_USED_ONLY_ONCE', priorities.HIGH_PRIORITY, filename, lineno,
                            'Random object created and used only once')
            )


class RandomD2IDetector(Detector):
    def __init__(self):
        self.pattern = regex.compile(r'\(\s*int\s*\)\s*(\w+)\.(?:random|nextDouble|nextFloat)\(\s*\)')
        Detector.__init__(self)

    def match(self, linecontent: str, filename: str, lineno: int, **kwargs):
        m = self.pattern.search(linecontent.strip())
        if m:
            obj = m.groups()[0].strip().lower()
            if obj == 'math' or obj == 'r' or 'rand' in obj:
                self.bug_accumulator.append(
                    BugInstance('RV_01_TO_INT', priorities.HIGH_PRIORITY, filename, lineno,
                                'Random value from 0 to 1 is coerced to the integer 0')
                )


class StringCtorDetector(Detector):
    def __init__(self):
        self.pattern = regex.compile(r'new\s+String\s*(?P<aux1>\(((?:[^()]++|(?&aux1))*)\))')
        Detector.__init__(self)

    def match(self, linecontent: str, filename: str, lineno: int, **kwargs):
        m = self.pattern.search(linecontent.strip())
        if m:
            groups = m.groups()
            assert len(groups) == 2
            if not groups[1] or not groups[1].strip():
                self.bug_accumulator.append(BugInstance('DM_STRING_VOID_CTOR', priorities.MEDIUM_PRIORITY,
                                                        filename, lineno,
                                                        'Method invokes inefficient new String() constructor'))
            else:
                if groups[1].strip().startswith('"'):
                    self.bug_accumulator.append(BugInstance('DM_STRING_CTOR', priorities.MEDIUM_PRIORITY,
                                                            filename, lineno,
                                                            'Method invokes inefficient new String(String) constructor'))


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

    def match(self, linecontent: str, filename: str, lineno: int, **kwargs):
        if not all(key in linecontent for key in ('Math', 'min', 'max')):
            return

        m1 = self.pattern.search(linecontent)
        if m1:
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
                    const_1 = str_to_float(arg_str_1[m2.end()+1:])
                else:
                    const_1 = str_to_float(arg_str_1[:m2.start()-1])

                inner_args = arg_str_2.split(',')
                if len(inner_args) != 2:
                    log_message(f'[InvalidMinMaxDetector] More than one commas for {linecontent}', 'error')
                    return

                for arg in inner_args:
                    const_2 = str_to_float(arg)
                    if const_2 is not None:
                        break

                if all(const is not None for const in (const_1, const_2)):
                    if outer_method == 'min':  # Math.min(const_1, Math.max(const_2, variable))
                        upper_bound = const_1
                        lower_bound = const_2
                    else:   # Math.max(const_1, Math.min(const_2, variable))
                        upper_bound = const_2
                        lower_bound = const_1

                    if upper_bound < lower_bound:
                        self.bug_accumulator.append(BugInstance('DM_INVALID_MIN_MAX', priorities.HIGH_PRIORITY,
                                                                filename, lineno,
                                                                'Incorrect combination of Math.max and Math.min'))
