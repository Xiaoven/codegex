import regex

from patterns.models import priorities
from patterns.models.bug_instance import BugInstance
from patterns.models.detectors import Detector
from utils import convert_str_to_int


class BadMonthDetector(Detector):
    def __init__(self):
        self.date = regex.compile(r'\b([\w$]+)\.setMonth\s*\((\d+)\s*\)')
        self.calendar = regex.compile(r'\b([\w$]+)\.set\s*\(([^,]+,\s*(\d+)\s*[,)])')
        self.gre_calendar = regex.compile(r'new\s+GregorianCalendar\s*\([^,]+,\s*(\d+)\s*,')
        Detector.__init__(self)

    def match(self, context):
        fire = False
        instance_name = None
        month = None
        priority = priorities.MEDIUM_PRIORITY

        line_content = context.cur_line.content
        if 'setMonth' in line_content:
            m = self.date.search(line_content)
            if m:
                fire = True
                g = m.groups()
                instance_name = g[0]
                month = int(g[1])
                priority = priorities.HIGH_PRIORITY
        elif 'set' in line_content:
            if 'calendar' in line_content.lower():  # To temporarily reduce unnecessary matches
                m = self.calendar.search(line_content)
                if m:
                    g = m.groups()

                    # TODO: find object type of instance_name by local search
                    if (g[1].endswith(')') and 'Calendar.MONTH' in g[1]) or \
                            (g[1].endswith(',') and 'calendar' in g[0].lower()):
                        fire = True
                        instance_name = g[0]
                        month = int(g[2])
        elif 'GregorianCalendar' in line_content and 'new' in line_content:
            m = self.gre_calendar.search(line_content)
            if m:
                fire = True
                month = int(m.groups()[0])

        if fire:
            if month < 0 or month > 11:
                self.bug_accumulator.append(BugInstance('DMI_BAD_MONTH', priority, context.cur_patch.name,
                                                        context.cur_line.lineno[1],
                                                        'Bad constant value for month.'))

                
class ShiftAddPriorityDetector(Detector):
    def __init__(self):
        self.pattern = regex.compile(r'\b[\w$]+\s*<<\s*([\w$]+)\s*[+-]\s*[\w$]+')
        Detector.__init__(self)

    def match(self, context):
        line_content = context.cur_line.content
        if '<<' not in line_content and '+' not in line_content:
            return

        m = self.pattern.search(line_content)
        if m:
            priority = priorities.LOW_PRIORITY
            const = convert_str_to_int(m.groups()[0])

            if const is not None:
                # If (foo << 32 + var) encountered for ISHL (left shift for int), then((foo << 32) + var) is absolutely
                # meaningless, but(foo << (32 + var)) can be meaningful for negative var values.
                # The same for LSHL (left shift for long)
                if const == 32 or const == 64:
                    return

                if const == 8:
                    priority = priorities.MEDIUM_PRIORITY

            self.bug_accumulator.append(BugInstance('BSHIFT_WRONG_ADD_PRIORITY', priority, context.cur_patch.name,
                                                    context.cur_line.lineno[1],
                                                    'Possible bad parsing of shift operation.'))


class OverwrittenIncrementDetector(Detector):
    def __init__(self):
        # 提取'='左右操作数
        self.pattern = regex.compile(
            r'(\b[\w+$]+)\s*=([\w\s+\-*\/]+)'
        )
        Detector.__init__(self)

    def match(self, context):
        line_content = context.cur_line.content
        strip_line = line_content.strip()
        if '=' in strip_line and any(op in strip_line for op in ('++', '--')):
            its = self.pattern.finditer(strip_line)
            for m in its:
                op_1 = m.groups()[0].strip()  # m.groups()[1] is the result of named pattern
                op_2 = m.groups()[1].strip()
                # 四种可能的匹配 '++a', '--a', 'a++', 'a--'
                pattern_inc = regex.compile(r'\+\+\s*{}|--\s*{}|{}\s*\+\+|{}\s*--'.format(op_1, op_1, op_1, op_1))
                if pattern_inc.search(op_2):
                    self.bug_accumulator.append(
                        BugInstance('DLS_OVERWRITTEN_INCREMENT', priorities.HIGH_PRIORITY,
                                    context.cur_patch.name, context.cur_line.lineno[1],
                                    "DLS: Overwritten increment")
                    )
                    break
