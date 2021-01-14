import regex
from patterns.models.bug_instance import BugInstance
from patterns.models.detectors import Detector
from patterns.models import priorities


class FindBadCastDetector(Detector):
    def __init__(self):
        self.pattern = regex.compile(r'\(\s*(?:(\w+))(\[\])+\)\s*.*\.toArray\s*\(\s*\)')
        self.pattern_ex = regex.compile(r'Arrays\.asList\(.*\)\.toArray\(')
        Detector.__init__(self)

    def match(self, linecontent: str, filename: str, lineno: int, **kwargs):
        strip_line = linecontent.strip()
        if 'toArray(' in strip_line:
            if 'Arrays.asList(' in strip_line:
                if self.pattern_ex.search(strip_line):
                    return
            if self.pattern.search(strip_line):
                its = self.pattern.finditer(strip_line)
                for m in its:
                    type_name = m.groups()[0]
                    print("*****", type_name)
                    if type_name == 'Object':
                        return
                    self.bug_accumulator.append(
                        BugInstance('BC_IMPOSSIBLE_DOWNCAST_OF_TOARRAY', priorities.HIGH_PRIORITY,
                                    filename, lineno,
                                    "BC: Impossible downcast of toArray() result")
                    )
