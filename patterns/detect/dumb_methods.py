import regex

from patterns.detectors import ParentDetector, SubDetector
from patterns.bug_instance import BugInstance
import patterns.priorities as Priorities


class DumbMethods(ParentDetector):
    def __init__(self):
        ParentDetector.__init__(self, [
            FinalizerOnExitSubDetector(),
            RandomOnceSubDetector()
        ])


class FinalizerOnExitSubDetector(SubDetector):
    def __init__(self):
        self.pattern = regex.compile('(\w*)\.*runFinalizersOnExit\(')
        SubDetector.__init__(self)

    def match(self, linecontent: str, filename: str, lineno: int):
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
        self.pattern = regex.compile('new\s+[\w\.]*Random(?:(?P<aux1>\((?:[^()]++|(?&aux1))*\)))++\.next\w*\(\s*\)')
        SubDetector.__init__(self)

    def match(self, linecontent: str, filename: str, lineno: int):
        m = self.pattern.search(linecontent)
        if m:
            self.bug_accumulator.append(
                BugInstance('DMI_RANDOM_USED_ONLY_ONCE', Priorities.HIGH_PRIORITY, filename, lineno,
                            'Random object created and used only once')
            )
