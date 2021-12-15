import regex
from patterns.models.priorities import *
from patterns.models.bug_instance import BugInstance
from patterns.models.detectors import Detector, get_exact_lineno


class DontJustCheckReadlineDetector(Detector):
    def __init__(self):
        self.pattern = regex.compile(r'\b\.readLine\s*\(\s*\)\s+!=\s+null\b')
        Detector.__init__(self)

    def match(self, context):
        line_content = context.cur_line.content
        if not all(key in line_content for key in ('readLine', 'null')):
            return
        m = self.pattern.search(line_content)
        if m:
            line_no = get_exact_lineno(m.end(0), context.cur_line)[1]
            self.bug_accumulator.append(
                BugInstance('RV_DONT_JUST_NULL_CHECK_READLINE', LOW_PRIORITY, context.cur_patch.name,
                            line_no, 'Method discards result of readLine after checking if it is non-null', sha=context.cur_patch.sha,
                            line_content=context.cur_line.content)
            )