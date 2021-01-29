import regex
from patterns.models.bug_instance import BugInstance
from patterns.models.detectors import Detector
from patterns.models import priorities


class FloatEqualityDetector(Detector):
    def __init__(self):
        self.pattern_op = regex.compile(
            r'(\b\w[\w.]*(?P<aux1>\((?:[^()]++|(?&aux1))*\))*)\s*[<>!=]+\s*(\b\w[\w.]*(?&aux1)*)')
        Detector.__init__(self)

    def match(self, context):
        line_content = context.cur_line.content
        strip_line = line_content.strip()
        if 'NaN' in strip_line \
                and any(op in line_content for op in ('>', '<', '>=', '<=', '==', '!=')):
            its = self.pattern_op.finditer(strip_line)
            for m in its:
                op_1 = m.groups()[0]  # m.groups()[1] is the result of named pattern
                op_2 = m.groups()[2]
                if any(op in ('Float.NaN', 'Double.NaN') for op in (op_1, op_2)):
                    self.bug_accumulator.append(
                        BugInstance('FE_TEST_IF_EQUAL_TO_NOT_A_NUMBER', priorities.HIGH_PRIORITY,
                                    context.cur_patch.name, context.cur_line.lineno[1],
                                    "Doomed test for equality to NaN")
                    )
                    return
