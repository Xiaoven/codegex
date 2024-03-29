import regex

from codegex.models.priorities import *
from codegex.models.bug_instance import BugInstance
from codegex.models.detectors import Detector, get_exact_lineno
from codegex.utils.utils import get_string_ranges, in_range


class UselessControlFlowNextLineDetector(Detector):
    def __init__(self):
        self.pattern = regex.compile(r'\b(?:if|for)\s*(?P<aux>\(((?:[^()]++|(?&aux))*)\))\s*;')
        Detector.__init__(self)

    def match(self, context):
        line_content = context.cur_line.content
        if 'if' in line_content or 'for' in line_content:
            m = self.pattern.search(line_content)
            if m and not in_range(m.start(0), get_string_ranges(line_content)):
                line_no = get_exact_lineno(m.end(0), context.cur_line)[1]
                # cannot retrieve branchLineNumber, targetLineNumber and nextLine
                self.bug_accumulator.append(
                    BugInstance('UCF_USELESS_CONTROL_FLOW_NEXT_LINE', MEDIUM_PRIORITY, context.cur_patch.name, line_no,
                                'Useless control flow to next line',
                                sha=context.cur_patch.sha,
                                line_content=context.cur_line.content)
                )

