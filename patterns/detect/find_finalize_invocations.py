import re

from patterns.detectors import Detector
from patterns.bug_instance import BugInstance
import patterns.priorities as Priorities
from patterns.utils import is_comment


class FiExplicitInvocation(Detector):
    def __init__(self):
        self.pattern = re.compile('\.finalize\s*\(\s*\)\s*;')

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

                line_content = line_content.strip()
                m = self.pattern.search(line_content)
                if m:
                    self.bug_accumulator.append(
                        BugInstance('FI_EXPLICIT_INVOCATION', Priorities.HIGH_PRIORITY, patch.name, hunk.lines[i].lineno[1],
                                    'Explicit invocation of Object.finalize()')
                    )
