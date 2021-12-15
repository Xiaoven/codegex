import regex
from patterns.models.priorities import *
from patterns.models.bug_instance import BugInstance
from patterns.models.detectors import Detector, get_exact_lineno


class InefficientIndexOfDetector(Detector):
    def __init__(self):
        self.pattern = regex.compile(r'\b\.(?:lastIndexOf|indexOf)\s*\(\s*\".\"')
        Detector.__init__(self)

    def match(self, context):
        line_content = context.cur_line.content
        if not any(key in line_content for key in ('lastIndexOf', 'indexOf')):
            return
        m = self.pattern.search(line_content)
        if m:
            line_no = get_exact_lineno(m.end(0), context.cur_line)[1]
            self.bug_accumulator.append(
                BugInstance('IIO_INEFFICIENT_LAST_INDEX_OF', LOW_PRIORITY, context.cur_patch.name,
                            line_no, 'Inefficient use of String.lastIndexOf(String)', sha=context.cur_patch.sha,
                            line_content=context.cur_line.content))
