import re

from patterns.detectors import Detector
from patterns.bug_instance import BugInstance
import patterns.priorities as Priorities


class NewLineDetector(Detector):
    def __init__(self):
        super().__init__()
        self.p = re.compile(r'(?:(?:String\.format)|printf)\([\w.\s()]*,?\s*"([^"]*)"\s*')

    def match(self, linecontent: str, filename: str, lineno: int, get_exact_lineno=None):
        m = self.p.search(linecontent)
        if m:
            format_str = m.groups()[0]

            if '\\n' in format_str:
                if get_exact_lineno:
                    tmp = get_exact_lineno(format_str)
                    if tmp:
                        lineno = tmp[1]

                self.bug_accumulator.append(
                    BugInstance('VA_FORMAT_STRING_USES_NEWLINE', Priorities.MEDIUM_PRIORITY,
                                filename, lineno,
                                'Format string should use %n rather than \\n')
                )
