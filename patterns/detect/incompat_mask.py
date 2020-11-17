from patterns.utils import is_comment
import patterns.priorities as Priorities
from patterns.detectors import Detector
from patterns.bug_instance import BugInstance
import regex


class BitSignedCheckAndBitAndZZ(Detector):
    def __init__(self):
        self.regexpSign = regex.compile(r'\(\s*((?:(?P<aux1>\((?:[^()]++|(?&aux1))*\))|[\w.])++)\s*&\s*((?:(?&aux1)|[\w.])+)\s*\)\s*>\s*0')
        self.regexpZZ = regex.compile(
            r'\(\s*((?:(?P<aux1>\((?:[^()]++|(?&aux1))*\))|[\w.])++)\s*&\s*0\s*\)\s*==\s*0')

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
                containsSign = self.regexpSign.search(line_content)
                containsZZ = self.regexpZZ.search(line_content)
                if containsSign:
                    bug_ins = BugInstance("BIT_SIGNED_CHECK", Priorities.IGNORE_PRIORITY, file_name,
                                          hunk.lines[i].lineno[1], 'There may be a sign mistake. You '
                                                                   'can replace >0 with !=0 ')
                    self.bug_accumulator.append(bug_ins)
                if containsZZ:
                    bug_ins = BugInstance("BIT_AND_ZZ", Priorities.HIGH_PRIORITY, file_name,
                                          hunk.lines[i].lineno[1], 'It will always be equal like \'var & 0 == 0\'')
                    self.bug_accumulator.append(bug_ins)
