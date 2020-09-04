import re

from patterns.detectors import Detector
from patterns.bug_instance import BugInstance
import patterns.priorities as Priorities
from patterns.utils import is_comment


class DmRunFinalizerOnExit(Detector):
    def __init__(self):
        self.pattern = re.compile('(\w*)\.*runFinalizersOnExit\(')

    def _visit_patch(self, patch):
        for hunk in patch:
            for i in range(len(hunk.lines)):
                # detect all lines in the patch rather than the addition
                if i in hunk.dellines:
                    continue

                line_content = hunk.lines[i].content
                if i in hunk.addlines:
                    line_content = line_content[1:]  # remove "+"

                if is_comment(line_content):
                    continue

                line_content = line_content.strip()
                m = self.pattern.search(line_content)
                if m:
                    pkg_name = m.groups()[0]
                    confidence = Priorities.HIGH_PRIORITY
                    if pkg_name == 'System' or 'Runtime':
                        confidence = Priorities.NORMAL_PRIORITY

                    self.bug_accumulator.append(
                        BugInstance('DM_RUN_FINALIZERS_ON_EXIT', confidence, patch.name, hunk.lines[i].lineno[1],
                                    'Method invokes dangerous method runFinalizersOnExit')
                    )
