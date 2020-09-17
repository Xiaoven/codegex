import patterns.priorities as Priorities
from patterns.detectors import ParentDetector
from patterns.detectors import SubDetector
from patterns.bug_instance import BugInstance
import regex


class IncompatMaskMethods(ParentDetector):
    def __init__(self):
        ParentDetector.__init__(self, [
            BitSignedCheckDetector(),
            BitAndZZDetector()
        ])


class BitSignedCheckDetector(SubDetector):
    def __init__(self):
        self.pattern = regex.compile(
            '\(\s*((?:(?P<aux1>\((?:[^()]++|(?&aux1))*\))|[\w.])++)\s*&\s*((?:(?&aux1)|[\w.])+)\s*\)\s*>\s*0')
        SubDetector.__init__(self)

    def match(self, linecontent: str, filename: str, lineno: int):
        m = self.pattern.search(linecontent)
        if m:
            self.bug_accumulator.append(
                BugInstance("BIT_SIGNED_CHECK", Priorities.IGNORE_PRIORITY, filename,
                            lineno, 'There may be a sign mistake. You '
                                    'can replace >0 with !=0 ')
            )


class BitAndZZDetector(SubDetector):
    def __init__(self):
        self.pattern = regex.compile('\(\s*((?:(?P<aux1>\((?:[^()]++|(?&aux1))*\))|[\w.])++)\s*&\s*0\s*\)\s*==\s*0')
        SubDetector.__init__(self)

    def match(self, linecontent: str, filename: str, lineno: int):
        m = self.pattern.search(linecontent)
        if m:
            self.bug_accumulator.append(
                BugInstance("BIT_AND_ZZ", Priorities.HIGH_PRIORITY, filename,
                            lineno, 'It will always be equal like \'var & 0 == 0\'')
            )
