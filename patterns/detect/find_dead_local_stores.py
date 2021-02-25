import re

from patterns.models.bug_instance import BugInstance
from patterns.models.detectors import Detector, get_exact_lineno
import patterns.models.priorities as Priorities
from utils import get_string_ranges, in_range


class FindDeadLocalIncrementInReturn(Detector):
    def __init__(self):
        self.pattern = re.compile(r'^\s*return\s+([\w$]+)(?:\+\+|--)\s*;')
        Detector.__init__(self)

    def match(self, context):
        line_content = context.cur_line.content
        if all(key not in line_content for key in ('++', '--')):
            return
        m = self.pattern.search(line_content)
        if m:
            string_ranges = get_string_ranges(line_content)
            if in_range(m.start(0), string_ranges):
                return

            var_name = m.groups()[0]

            # TODO: enhance with local search
            priority = Priorities.MEDIUM_PRIORITY
            if var_name.startswith('$'):
                priority = Priorities.LOW_PRIORITY

            line_no = get_exact_lineno(m.end(0)-1, context.cur_line)[1]
            self.bug_accumulator.append(
                BugInstance('DLS_DEAD_LOCAL_INCREMENT_IN_RETURN', priority, context.cur_patch.name,
                            line_no, 'Useless increment in return statement', sha=context.cur_patch.sha)
            )

