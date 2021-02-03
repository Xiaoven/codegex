import re

from patterns.models.bug_instance import BugInstance
from patterns.models.detectors import Detector
import patterns.models.priorities as Priorities


class FindDeadLocalIncrementInReturn(Detector):
    def __init__(self):
        self.pattern = re.compile(r'return\s+([\w$]+)(?:\+\+|--)\s*;')
        Detector.__init__(self)

    def match(self, context):
        line_content = context.cur_line.content
        if all(key not in line_content for key in ('++', '--')):
            return
        m = self.pattern.match(line_content.strip())
        if m:
            var_name = m.groups()[0]

            # TODO: enhance with local search
            priority = Priorities.MEDIUM_PRIORITY
            if var_name.startswith('$'):
                priority = Priorities.LOW_PRIORITY

            self.bug_accumulator.append(
                BugInstance('DLS_DEAD_LOCAL_INCREMENT_IN_RETURN', priority, context.cur_patch.name,
                            context.cur_line.lineno[1], 'Useless increment in return statement',
                            sha=context.cur_patch.sha)
            )

