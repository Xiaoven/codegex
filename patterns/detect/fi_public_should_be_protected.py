import re

from patterns.detectors import Detector
from patterns.bug_instance import BugInstance
import patterns.priorities as Priorities
from patterns.utils import is_comment


class FiPublicShouldBeProtected(Detector):
    def __init__(self):
        self.pattern = re.compile('public\s+void\s+finalize\(\s*\)')

    def _visit_patch(self, patch):
        for hunk in patch:
            for i in range(len(hunk.lines)):
                if i in hunk.dellines:
                    continue

                line_content = hunk.lines[i].content
                if i in hunk.addlines:
                    line_content = line_content[1:]  # remove "+"

                if is_comment(line_content):
                    continue

                match = self.pattern.search(line_content)
                if match:
                    self.bug_accumulator.append(BugInstance('FI_PUBLIC_SHOULD_BE_PROTECTED', Priorities.NORMAL_PRIORITY,
                                                            patch.name, hunk.lines[i].lineno[1],
                                                            'Finalizer should be protected, not public'))
