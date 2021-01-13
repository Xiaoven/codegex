import regex
from patterns.models.bug_instance import BugInstance
from patterns.models.detectors import Detector
from patterns.models import priorities


class FloatEqualityDetector(Detector):
    def __init__(self):
        self.pattern = regex.compile(
            r'((?:(?P<aux1>\((?:[^()]++|(?&aux1))*\))|[\w."])++)\s*[<>!=]+\s*((?:(?&aux1)|[\w."])+)')
        self.float_NaN = ('Float.NaN', 'Double.NaN')
        Detector.__init__(self)

    def match(self, linecontent: str, filename: str, lineno: int, **kwargs):
        if any(op in linecontent for op in ('>', '<', '>=', '<=', '==', '!=')):
            its = self.pattern.finditer(linecontent.strip())
            for m in its:
                op_1 = m.groups()[0]  # m.groups()[1] is the result of named pattern
                op_2 = m.groups()[2]
                if op_1 in self.float_NaN and op_2 in self.float_NaN:
                    return
                if op_1 in self.float_NaN or op_2 in self.float_NaN:
                    self.bug_accumulator.append(
                    BugInstance('FE_TEST_IF_EQUAL_TO_NOT_A_NUMBER', priorities.HIGH_PRIORITY,
                                filename, lineno,
                                "Doomed test for equality to NaN")
                    )
                break