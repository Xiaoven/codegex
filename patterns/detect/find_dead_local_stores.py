import re

from patterns.models.bug_instance import BugInstance
from patterns.models.detectors import Detector
import patterns.models.priorities as Priorities


class FindDeadLocalIncrementInReturn(Detector):
    def __init__(self):
        self.pattern = re.compile(r'return\s+([\w$]+)(?:\+\+|--)\s*;')
        Detector.__init__(self)

    def match(self, linecontent: str, filename: str, lineno: int, **kwargs):
        if all(key not in linecontent for key in ('++', '--')):
            return
        m = self.pattern.match(linecontent.strip())
        if m:
            var_name = m.groups()[0]

            # TODO: enhance with local search
            priority = Priorities.MEDIUM_PRIORITY
            if var_name.startswith('$'):
                priority = Priorities.LOW_PRIORITY

            self.bug_accumulator.append(
                BugInstance('DLS_DEAD_LOCAL_INCREMENT_IN_RETURN', Priorities.MEDIUM_PRIORITY, filename, lineno,
                            'Useless increment in return statement')
            )

