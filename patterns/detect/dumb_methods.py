import regex

from patterns.detectors import ParentDetector, SubDetector
from patterns.bug_instance import BugInstance
import patterns.priorities as Priorities


class DumbMethods(ParentDetector):
    def __init__(self):
        ParentDetector.__init__(self, [
            FinalizerOnExitSubDetector(),
            RandomOnceSubDetector(),
            StringCtorSubDetector(),
            RandomD2ISubDetector()
        ])


class FinalizerOnExitSubDetector(SubDetector):
    def __init__(self):
        self.pattern = regex.compile(r'(\w*)\.*runFinalizersOnExit\(')
        SubDetector.__init__(self)

    def match(self, linecontent: str, filename: str, lineno: int, get_exact_lineno=None):
        m = self.pattern.search(linecontent)
        if m:
            pkg_name = m.groups()[0]
            confidence = Priorities.HIGH_PRIORITY
            if pkg_name == 'System' or 'Runtime':
                confidence = Priorities.NORMAL_PRIORITY

            self.bug_accumulator.append(
                BugInstance('DM_RUN_FINALIZERS_ON_EXIT', confidence, filename, lineno,
                            'Method invokes dangerous method runFinalizersOnExit')
            )


class RandomOnceSubDetector(SubDetector):
    def __init__(self):
        self.pattern = regex.compile(r'new\s+[\w\.]*Random(?:(?P<aux1>\((?:[^()]++|(?&aux1))*\)))++\.next\w*\(\s*\)')
        SubDetector.__init__(self)

    def match(self, linecontent: str, filename: str, lineno: int, get_exact_lineno=None):
        m = self.pattern.search(linecontent)
        if m:
            self.bug_accumulator.append(
                BugInstance('DMI_RANDOM_USED_ONLY_ONCE', Priorities.HIGH_PRIORITY, filename, lineno,
                            'Random object created and used only once')
            )


class RandomD2ISubDetector(SubDetector):
    def __init__(self):
        self.pattern = regex.compile(r'\(\s*int\s*\)\s*(\w+)\.(?:random|nextDouble|nextFloat)\(\s*\)')
        SubDetector.__init__(self)

    def match(self, linecontent: str, filename: str, lineno: int, get_exact_lineno=None):
        m = self.pattern.search(linecontent)
        if m:
            obj = m.groups()[0].strip().lower()
            if obj == 'math' or obj == 'r' or 'rand' in obj:
                self.bug_accumulator.append(
                    BugInstance('RV_01_TO_INT', Priorities.HIGH_PRIORITY, filename, lineno,
                                'Random value from 0 to 1 is coerced to the integer 0')
                )


class StringCtorSubDetector(SubDetector):
    def __init__(self):
        self.pattern = regex.compile(r'new\s+String\s*(?P<aux1>\(((?:[^()]++|(?&aux1))*)\))')
        SubDetector.__init__(self)

    def match(self, linecontent: str, filename: str, lineno: int, get_exact_lineno=None):
        m = self.pattern.search(linecontent)
        if m:
            groups = m.groups()
            assert len(groups) == 2
            if not groups[1] or not groups[1].strip():
                self.bug_accumulator.append(BugInstance('DM_STRING_VOID_CTOR', Priorities.NORMAL_PRIORITY,
                                                        filename, lineno,
                                                        'Method invokes inefficient new String() constructor'))
            else:
                if '"' == groups[1].strip()[0] and '"' == groups[1].strip()[-1]:
                    self.bug_accumulator.append(BugInstance('DM_STRING_CTOR', Priorities.NORMAL_PRIORITY,
                                                            filename, lineno,
                                                            'Method invokes inefficient new String(String) constructor'))
