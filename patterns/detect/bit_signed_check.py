from patterns.utils import is_comment
import patterns.priorities as Priorities
from patterns.detectors import Detector
from patterns.bug_instance import BugInstance
import re


class ChekBitSigned(Detector):
    def __init__(self):
        self.regexp1 = re.compile('&{1}')
        self.regexp2 = re.compile('\s*0(?!(\.|\w))')

    def _visit_patch(self, patch):
        file_name = patch.name

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
                containsOp = bool(self.regexp1.search(line_content))
                containsZero = bool(self.regexp2.search(line_content))
                if containsOp and containsZero:
                    bug_ins = BugInstance("BIT_SIGNED_CHECK", Priorities.IGNORE_PRIORITY, file_name,
                                          hunk.lines[i].lineno[1], 'There may be a sign mistake. You '
                                                                   'can replace >0 with !=0 ')
                    self.bug_accumulator.append(bug_ins)
