import re

from patterns.detectors import ParentDetector, SubDetector
from patterns.bug_instance import BugInstance
import patterns.priorities as Priorities


class FormatStringChecker(ParentDetector):
    def __init__(self):
        ParentDetector.__init__(self, [NewLineSubDetector()])


class NewLineSubDetector(SubDetector):
    def __init__(self):
        super().__init__()
        self.p = re.compile(r'(?:(?:String\.format)|printf)\([\w\.\s\(\)]*,?\s*"([^"]*)"\s*')

    def match(self, linecontent: str, filename: str, lineno: int, get_exact_lineno=None):
        m = self.p.search(linecontent)
        if m:
            format_str = m.groups()[0]

            if '\\n' in format_str:
                final_lineno = lineno
                if get_exact_lineno:
                    final_lineno = get_exact_lineno(format_str)[1]

                self.bug_accumulator.append(
                    BugInstance('VA_FORMAT_STRING_USES_NEWLINE', Priorities.NORMAL_PRIORITY,
                                filename, final_lineno,
                                'Format string should use %n rather than \\n')
                )
