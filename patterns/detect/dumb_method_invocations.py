import regex

from patterns.models.priorities import *
from patterns.models.bug_instance import BugInstance
from patterns.models.detectors import Detector, get_exact_lineno


class UselessSubstringDetector(Detector):
    def __init__(self):
        self.pattern = regex.compile(r'\.\s*substring\s*\(\s*0\s*\)')
        Detector.__init__(self)

    def match(self, context):
        line_content = context.cur_line.content
        m = self.pattern.search(line_content)
        if m:
            line_no = get_exact_lineno(m.end(0), context.cur_line)[1]
            self.bug_accumulator.append(
                BugInstance('DMI_USELESS_SUBSTRING', MEDIUM_PRIORITY, context.cur_patch.name, line_no,
                            'This code invokes substring(0) on a String, which returns the original value.', sha=context.cur_patch.sha,
                            line_content=context.cur_line.content)
            )