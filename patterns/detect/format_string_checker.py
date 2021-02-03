import re

from patterns.models.detectors import Detector
from patterns.models.bug_instance import BugInstance
from patterns.models import priorities


class NewLineDetector(Detector):
    def __init__(self):
        super().__init__()
        self.p = re.compile(r'(?:(?:String\.format)|printf)\([\w.\s()]*,?\s*"([^"]*)"\s*')

    def match(self, context):
        line_content = context.cur_line.content
        line_no = context.cur_line.lineno[1]
        m = self.p.search(line_content.strip())
        if m:
            format_str = m.groups()[0]

            if '\\n' in format_str:
                if hasattr(context.cur_line, 'get_exact_lineno'):
                    tmp = context.cur_line.get_exact_lineno(format_str)
                    if tmp:
                        line_no = tmp[1]

                self.bug_accumulator.append(
                    BugInstance('VA_FORMAT_STRING_USES_NEWLINE', priorities.MEDIUM_PRIORITY,
                                context.cur_patch.name, line_no,
                                'Format string should use %n rather than \\n', sha=context.cur_patch.sha)
                )
