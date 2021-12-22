import regex
from models.priorities import *
from models.bug_instance import BugInstance
from models.detectors import Detector, get_exact_lineno
from utils.utils import in_range, get_string_ranges


class DontJustCheckReadlineDetector(Detector):
    def __init__(self):
        self.pattern = regex.compile(r'(?P<op>\bnull|\b\w+\s*\.\s*readLine\s*\(\s*\))\s*[!=]=\s*((?&op))')
        Detector.__init__(self)

    def match(self, context):
        line_content = context.cur_line.content
        if not all(key in line_content for key in ('readLine', 'null')):
            return
        itr = self.pattern.finditer(line_content)
        for m in itr:
            print(m.groups())
            if not in_range(m.start(0), get_string_ranges(line_content)):
                op1 = m.group(1)
                op2 = m.group(2)
                if op1 == 'null' and 'readLine' in op2 or op2 == 'null' and 'readLine' in op1:
                    line_no = get_exact_lineno(m.end(0), context.cur_line)[1]
                    self.bug_accumulator.append(
                        BugInstance('RV_DONT_JUST_NULL_CHECK_READLINE', MEDIUM_PRIORITY, context.cur_patch.name,
                                    line_no, 'Method discards result of readLine after checking if it is non-null', sha=context.cur_patch.sha,
                                    line_content=context.cur_line.content)
                    )
                    break
