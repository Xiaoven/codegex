import patterns.priorities as Priorities
from patterns.detectors import Detector
from patterns.bug_instance import BugInstance
import regex


class BitSignedCheck(Detector):
    def __init__(self):
        self.regexpSign = regex.compile(
            r'\(\s*((?:(?P<aux1>\((?:[^()]++|(?&aux1))*\))|[\w.])++)\s*&\s*((?:(?&aux1)|[\w.])+)\s*\)\s*>\s*0')
        Detector.__init__(self)

    def match(self, linecontent: str, filename: str, lineno: int, get_exact_lineno=None):
        containsSign = self.regexpSign.search(linecontent)

        if containsSign:
            bug_ins = BugInstance("BIT_SIGNED_CHECK", Priorities.IGNORE_PRIORITY, filename,
                                  lineno, 'There may be a sign mistake. You '
                                          'can replace >0 with !=0 ')
            self.bug_accumulator.append(bug_ins)


class BitSignedCheckAndBitAndZZDetector(Detector):
    def __init__(self):
        self.regexpZZ = regex.compile(
            r'\(\s*((?:(?P<aux1>\((?:[^()]++|(?&aux1))*\))|[\w.])++)\s*&\s*0\s*\)\s*==\s*0')
        Detector.__init__(self)

    def match(self, linecontent: str, filename: str, lineno: int, get_exact_lineno=None):
        containsZZ = self.regexpZZ.search(linecontent)
        if containsZZ:
            bug_ins = BugInstance("BIT_AND_ZZ", Priorities.HIGH_PRIORITY, filename,
                                  lineno, "It will always be equal like 'var & 0 == 0'")
            self.bug_accumulator.append(bug_ins)
