import re

from patterns.detectors import ParentDetector, SubDetector
from patterns.bug_instance import BugInstance
import patterns.priorities as Priorities


class FormatStringChecker(ParentDetector):
    def __init__(self):
        ParentDetector.__init__(self, [NewLineSubDetector()])


class NewLineSubDetector(SubDetector):
    def __init__(self):
        super().__init__()
        self.p = re.compile(r'(?:String\.format)\([\w\.\s\(\)]*,{0,1}\s*\"([^\"]*)\"\s*')
        self.relax_p = re.compile(r'(?:(?:(?:[fF]ormatter)|(?:[pP]rint[sS]tream)|(?:[wW]riter))\.(?:(?:format)|(?:printf)))\([\w\.\s\(\)]*,{0,1}\s*\"([^\"]*)\"\s*')

    def match(self, linecontent: str, filename: str, lineno: int, get_exact_lineno=None):
        m = self.p.search(linecontent)
        relax_m = self.relax_p.search(linecontent)
        if m:
            format_str = m.groups()[0]

            if '\\n' in format_str:
                final_lineno = lineno
                if get_exact_lineno:
                    final_lineno = get_exact_lineno(format_str)[1]
                idx_list = []

                for idx in range(len(format_str)):
                    if format_str[idx] == '\\' \
                            and idx + 1 < len(format_str) and format_str[idx + 1] == 'n' \
                            and (idx == 0 or (idx - 1 >= 0 and format_str[idx - 1] != '\\')):
                        idx_list.append(idx)
                if idx_list:
                    self.bug_accumulator.append(
                        BugInstance('VA_FORMAT_STRING_USES_NEWLINE', Priorities.NORMAL_PRIORITY,
                                    filename, final_lineno,
                                    'Format string should use %n rather than \\n')
                    )
        elif relax_m:
            format_str = relax_m.groups()[0]

            if '\\n' in format_str:
                final_lineno = lineno
                if get_exact_lineno:
                    final_lineno = get_exact_lineno(format_str)[1]
                idx_list = []

                for idx in range(len(format_str)):
                    if format_str[idx] == '\\' \
                            and idx + 1 < len(format_str) and format_str[idx + 1] == 'n' \
                            and (idx == 0 or (idx - 1 >= 0 and format_str[idx - 1] != '\\')):
                        idx_list.append(idx)
                if idx_list:
                    self.bug_accumulator.append(
                        BugInstance('VA_FORMAT_STRING_USES_NEWLINE', Priorities.EXP_PRIORITY,
                                    filename, final_lineno,
                                    'If java.io.PrintStream/java.util.Formatter/java.io.Writer are used,'
                                    'format string should use %n rather than \\n. Otherwise ignore this bug.')
                    )
