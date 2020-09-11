import regex

from patterns.detectors import Detector
from patterns.bug_instance import BugInstance
import patterns.priorities as Priorities
from patterns.utils import is_comment


class FindRefComparison(Detector):
    def __init__(self):
        self.comp_eq = regex.compile(
            '((?:(?P<aux1>\((?:[^()]++|(?&aux1))*\))|[\w.])++)\s*[!=]=\s*((?:(?&aux1)|[\w.])+)')
        self.bool_objs = ('Boolean.TRUE', 'Boolean.FALSE')

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
                m = self.comp_eq.search(line_content)
                if m:
                    op_1 = m.groups()[0]  # m.groups()[0] is the result of named pattern
                    op_2 = m.groups()[2]

                    if op_1 in self.bool_objs or op_2 in self.bool_objs:
                        self.bug_accumulator.append(
                            BugInstance('RC_REF_COMPARISON_BAD_PRACTICE_BOOLEAN', Priorities.NORMAL_PRIORITY,
                                        patch.name, hunk.lines[i].lineno[1],
                                        "Suspicious reference comparison of Boolean values")
                        )



