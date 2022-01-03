import regex
from codegex.models.priorities import *
from codegex.models.bug_instance import BugInstance
from codegex.models.detectors import Detector, get_exact_lineno


class InefficientIndexOfDetector(Detector):
    def __init__(self):
        self.pattern = regex.compile(r'\.\s*(lastIndexOf|indexOf)\s*\(\s*"."\s*[,)]')
        Detector.__init__(self)

    def match(self, context):
        line_content = context.cur_line.content
        if not any(key in line_content for key in ('lastIndexOf', 'indexOf')):
            return
        m = self.pattern.search(line_content)
        if m:
            line_no = get_exact_lineno(m.end(0), context.cur_line)[1]
            method_name = m.groups()[0]
            if method_name == 'lastIndexOf':
                self.bug_accumulator.append(
                    BugInstance('IIO_INEFFICIENT_LAST_INDEX_OF', LOW_PRIORITY, context.cur_patch.name,
                                line_no, 'Inefficient use of String.lastIndexOf(String)', sha=context.cur_patch.sha,
                                line_content=context.cur_line.content)
                )
            else:
                self.bug_accumulator.append(
                    BugInstance('IIO_INEFFICIENT_INDEX_OF', LOW_PRIORITY, context.cur_patch.name,
                                line_no, 'IIO: Inefficient use of String.indexOf(String)', sha=context.cur_patch.sha,
                                line_content=context.cur_line.content)
                )
