import regex

from patterns.models.detectors import Detector
from patterns.models.bug_instance import BugInstance
from patterns.models import priorities


class DontUseEnumDetector(Detector):
    def __init__(self):
        self.p = regex.compile(r'\b(enum|assert)\s*[^\w$\s(]')
        self.p_method = regex.compile(r'\b\w+[\s.]+(enum|assert)\s*\(')
        Detector.__init__(self)

    def match(self, linecontent: str, filename: str, lineno: int, **kwargs):
        strip_line = linecontent.strip()
        if not any(key in strip_line for key in ('assert', 'enum')):
            return

        if self.p.search(strip_line):
            self.bug_accumulator.append(
                BugInstance('NM_FUTURE_KEYWORD_USED_AS_IDENTIFIER', priorities.MEDIUM_PRIORITY, filename, lineno,
                            'Nm: Use of identifier that is a keyword in later versions of Java')
            )

        if self.p_method.search(strip_line):
            self.bug_accumulator.append(
                BugInstance('NM_FUTURE_KEYWORD_USED_AS_MEMBER_IDENTIFIER', priorities.MEDIUM_PRIORITY, filename, lineno,
                            'Nm: Use of identifier that is a keyword in later versions of Java')
            )