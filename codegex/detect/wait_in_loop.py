import regex

from codegex.models.bug_instance import BugInstance
from codegex.models.detectors import Detector, get_exact_lineno
from codegex.models.priorities import *
from codegex.utils.utils import in_range, get_string_ranges


class NotifyDetector(Detector):
    def __init__(self):
        Detector.__init__(self)
        self.pattern = regex.compile(r'\bnotify\s*\(\s*\)')

    def match(self, context):
        line_content = context.cur_line.content
        if 'notify' in line_content and 'notifyAll' not in line_content:
            m = self.pattern.search(line_content)
            if m and not in_range(m.start(0), get_string_ranges(line_content)):
                self.bug_accumulator.append(
                    BugInstance('NO_NOTIFY_NOT_NOTIFYALL', LOW_PRIORITY,
                                context.cur_patch.name, get_exact_lineno(m.end(0), context.cur_line)[1],
                                "Using notify() rather than notifyAll()",
                                sha=context.cur_patch.sha, line_content=context.cur_line.content)
                )
