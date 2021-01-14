import regex

from patterns.models import priorities
from patterns.models.bug_instance import BugInstance
from patterns.models.detectors import Detector


class BadMonthDetector(Detector):
    def __init__(self):
        self.date = regex.compile(r'\b([\w$]+)\.setMonth\s*\((\d+)\s*\)')
        self.calendar = regex.compile(r'\b([\w$]+)\.set\s*\(([^,]+,\s*(\d+)\s*[,)])')
        self.gre_calendar = regex.compile(r'new\s+GregorianCalendar\s*\([^,]+,\s*(\d+)\s*,')
        Detector.__init__(self)

    def match(self, linecontent: str, filename: str, lineno: int, **kwargs):
        fire = False
        instance_name = None
        month = None
        priority = priorities.MEDIUM_PRIORITY

        if 'setMonth' in linecontent:
            m = self.date.search(linecontent)
            if m:
                fire = True
                g = m.groups()
                instance_name = g[0]
                month = int(g[1])
                priority = priorities.HIGH_PRIORITY
        elif 'set' in linecontent:
            if 'calendar' in linecontent.lower():  # To temporarily reduce unnecessary matches
                m = self.calendar.search(linecontent)
                if m:
                    g = m.groups()

                    # TODO: find object type of instance_name by local search
                    if (g[1].endswith(')') and 'Calendar.MONTH' in g[1]) or \
                            (g[1].endswith(',') and 'calendar' in g[0].lower()):
                        fire = True
                        instance_name = g[0]
                        month = int(g[2])
        elif 'GregorianCalendar' in linecontent and 'new' in linecontent:
            m = self.gre_calendar.search(linecontent)
            if m:
                fire = True
                month = int(m.groups()[0])

        if fire:
            if month < 0 or month > 11:
                self.bug_accumulator.append(BugInstance('DMI_BAD_MONTH', priority, filename, lineno,
                                                        'Bad constant value for month.'))

class OverwrittenIncrementDetector(Detector):
    def __init__(self):
        # 提取'='左右操作数
        self.pattern = regex.compile(
            r'((?:(?P<aux1>\((?:[^()]++|(?&aux1))*\))|[\w])++)\s*=\s*((?:(?&aux1)|[\w\s+\-*\/])+)'
        )
        Detector.__init__(self)

    def match(self, linecontent: str, filename: str, lineno: int, **kwargs):
        strip_line = linecontent.strip()
        if '=' in strip_line and any(op in strip_line for op in ('++', '--')):
            its = self.pattern.finditer(strip_line)
            for m in its:
                op_1 = m.groups()[0]  # m.groups()[1] is the result of named pattern
                op_2 = m.groups()[2]
                # 四种可能的匹配 '++a', '--a', 'a++', 'a--'
                pattern_inc = regex.compile(r'\+\+\s*{}|\-\-\s*{}|\s*{}\+\+|\s*{}\-\-'.format(op_1, op_1, op_1, op_1))
                if pattern_inc.search(op_2):
                    self.bug_accumulator.append(
                    BugInstance('DLS_OVERWRITTEN_INCREMENT', priorities.HIGH_PRIORITY,
                                        filename, lineno,
                                        "DLS: Overwritten increment ")
                            )
                    break
