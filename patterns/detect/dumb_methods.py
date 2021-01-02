import regex

from patterns.models.detectors import Detector
from patterns.models.bug_instance import BugInstance
from patterns.models import priorities


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
