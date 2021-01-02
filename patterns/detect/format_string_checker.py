import re

from patterns.models.detectors import Detector
from patterns.models.bug_instance import BugInstance
from patterns.models import priorities


class NewLineDetector(Detector):
    def __init__(self):
        super().__init__()
        self.p = re.compile(r'(?:(?:String\.format)|printf)\([\w.\s()]*,?\s*"([^"]*)"\s*')

    def match(self, linecontent: str, filename: str, lineno: int, **kwargs):
        m = self.p.search(linecontent.strip())
        if m:
            format_str = m.groups()[0]

            if '\\n' in format_str:
                get_exact_lineno = kwargs.get('get_exact_lineno', None)
                if get_exact_lineno:
                    tmp = get_exact_lineno(format_str)
                    if tmp:
                        lineno = tmp[1]

                self.bug_accumulator.append(
                    BugInstance('VA_FORMAT_STRING_USES_NEWLINE', priorities.MEDIUM_PRIORITY,
                                filename, lineno,
                                'Format string should use %n rather than \\n')
                )
