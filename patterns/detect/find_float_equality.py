import regex
from patterns.models.bug_instance import BugInstance
from patterns.models.detectors import Detector
from patterns.models import priorities


class FloatEqualityDetector(Detector):
    def __init__(self):
        self.pattern_op = regex.compile(
            r'(\b\w[\w.]*(?P<aux1>\((?:[^()]++|(?&aux1))*\))*)\s*[<>!=]+\s*(\b\w[\w.]*(?&aux1)*)')
        self.pattern_nan = regex.compile(r'\b\w+\.NaN\b')
        Detector.__init__(self)

    def match(self, linecontent: str, filename: str, lineno: int, **kwargs):
        strip_line = linecontent.strip()
        if self.pattern_nan.search(strip_line) \
                and any(op in linecontent for op in ('>', '<', '>=', '<=', '==', '!=')):
            its = self.pattern_op.finditer(strip_line)
            for m in its:
                op_1 = m.groups()[0]  # m.groups()[1] is the result of named pattern
                op_2 = m.groups()[2]
                if self.is_float(op_1) or self.is_float(op_2):
                    self.bug_accumulator.append(
                    BugInstance('FE_TEST_IF_EQUAL_TO_NOT_A_NUMBER', priorities.HIGH_PRIORITY,
                                filename, lineno,
                                "Doomed test for equality to NaN")
                    )
                break

    def is_float(self, oprand:str):
        if "Double" in oprand or "Float" in oprand:
            return True
        else:
            return False