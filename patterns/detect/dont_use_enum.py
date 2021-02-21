import regex

from patterns.models.detectors import Detector
from patterns.models.bug_instance import BugInstance
from patterns.models import priorities
from utils import get_string_ranges, in_range


class DontUseEnumDetector(Detector):
    def __init__(self):
        self.p_identifier = regex.compile(r'\b\w+\b(?:\s+|(\s*\.\s*)?)(enum|assert)\s*(?(1)[^\w$\s]|\()')
        self.p = regex.compile(r'\b(?:enum|assert)\s*[^\w$\s(]')
        Detector.__init__(self)

    def match(self, context):
        strip_line = context.cur_line.content.strip()
        if not any(key in strip_line for key in ('assert', 'enum')):
            return

        string_range = get_string_ranges(strip_line)

        its = self.p_identifier.finditer(strip_line)
        for m in its:
            if not in_range(m.start(2), string_range):
                # In spotbugs, it checks methods and fields.
                # We check method definition and calls like `obj.field` or `obj.method()`
                self.bug_accumulator.append(
                    BugInstance('NM_FUTURE_KEYWORD_USED_AS_MEMBER_IDENTIFIER', priorities.MEDIUM_PRIORITY,
                                context.cur_patch.name, context.cur_line.lineno[1],
                                'Nm: Use of identifier that is a keyword in later versions of Java',
                                sha=context.cur_patch.sha)
                )
                return

        its = self.p.finditer(strip_line)
        for m in its:
            if not in_range(m.start(0), string_range):
                # In spotbugs, it checks local variables, here we check local variables and fields.
                self.bug_accumulator.append(
                    BugInstance('NM_FUTURE_KEYWORD_USED_AS_IDENTIFIER', priorities.MEDIUM_PRIORITY,
                                context.cur_patch.name, context.cur_line.lineno[1],
                                'Nm: Use of identifier that is a keyword in later versions of Java',
                                sha=context.cur_patch.sha)
                )
                return
