import regex

from patterns.detectors import Detector, SubDetector
from patterns.bug_instance import BugInstance
import patterns.priorities as Priorities
from patterns.utils import is_comment


class DumbMethods(Detector):
    def _visit_patch(self, patch):
        # init sub detectors
        subdetectors = [
            FinalizerOnExitSubDetector(),
            RandomOnceSubDetector()]

        # detect patch
        for hunk in patch:
            for i in range(len(hunk.lines)):
                # detect all lines in the patch rather than the addition
                if i in hunk.dellines:
                    continue

                line_content = hunk.lines[i].content
                if i in hunk.addlines:
                    line_content = line_content[1:]  # remove "+"

                line_content = line_content.strip()
                if not line_content or is_comment(line_content):
                    continue

                for detector in subdetectors:
                    detector.match(line_content, patch.name, hunk.lines[i].lineno[1])

        # collect bug instances
        for detector in subdetectors:
            if detector.bug_accumulator:
                self.bug_accumulator += detector.bug_accumulator



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
