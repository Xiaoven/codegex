import patterns.priorities as Priorities
from patterns.detectors import Detector
from patterns.bug_instance import BugInstance
import regex


class IncompatMaskDetector(Detector):
    def __init__(self):
        self.regexpSign = regex.compile(
            r'\(\s*(?:(?P<aux1>\((?:[^()]++|(?&aux1))*\))|[\w.])++\s*&\s*(?:(?&aux1)|[\w.])+\s*\)\s*(>|==)\s*0')
        Detector.__init__(self)

    def match(self, linecontent: str, filename: str, lineno: int, get_exact_lineno=None):
        if not all(op in linecontent for op in ['&', '0']) \
                and not any(op in linecontent for op in ['>', '==']):
            return

        containsSign = self.regexpSign.search(linecontent)

        if containsSign:
            p_type = None
            description = None
            priority = Priorities.HIGH_PRIORITY

            g = containsSign.groups()
            if g[-1] == '>':
                p_type = 'BIT_SIGNED_CHECK'
                description = 'There may be a sign mistake. You can replace >0 with !=0 '
            else:
                p_type = 'BIT_AND_ZZ'
                description = 'It will always be equal like "var & 0 == 0"'

            bug_ins = BugInstance(p_type, priority, filename,
                                  lineno, description)
            self.bug_accumulator.append(bug_ins)
