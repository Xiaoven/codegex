import re

from patterns.detectors import Detector
from patterns.bug_instance import BugInstance
import patterns.priorities as Priorities
from patterns.utils import is_comment


class FormatStringChecker(Detector):
    def __init__(self):
        self.p = re.compile(r'(?:(?:String\.format)|printf)\([\w\.\s\(\)]*,{0,1}\s*\"([^\"]*)\"\s*')
        self.relax_p = re.compile(r'(?:(?:(([F,f]ormatter)|([P,p]rintStream)|([W,w]riter))\.format))\([\w\.\s\(\)]*,{0,1}\s*\"([^\"]*)\"\s*')



    def _visit_patch(self, patch):
        for hunk in patch:
            last_line = ''  # non-empty or not none under multiline mode
            for i in range(len(hunk.lines)):
                # detect all lines in the patch rather than the addition
                if i in hunk.dellines:
                    continue

                line_content = hunk.lines[i].content
                if i in hunk.addlines:
                    line_content = line_content[1:]  # remove "+"

                line_content = line_content.strip()
                if (not line_content) or is_comment(line_content):
                    continue

                if last_line:
                    last_line += line_content
                else:
                    last_line = line_content

                m = self.p.search(last_line)
                relax_m = self.relax_p.search(last_line)

                if m:
                    format_str = m.groups()[0]
                    last_line = ''
                    idx_list = []
                    for idx in range(len(format_str)):
                        if format_str[idx] == '\\' and idx + 1 < len(format_str) and format_str[idx+1] == 'n'and (idx==0 or (idx-1>=0 and format_str[idx-1] != '\\')):
                            idx_list.append(i)

                    if idx_list:
                        self.bug_accumulator.append(
                            BugInstance('VA_FORMAT_STRING_USES_NEWLINE', Priorities.NORMAL_PRIORITY,
                                        patch.name, hunk.lines[i].lineno[1],
                                        'Format string should use %n rather than \\n')
                        )
                elif relax_m:
                    format_str = relax_m.groups()[4]
                    last_line = ''
                    idx_list = []
                    for idx in range(len(format_str)):
                        if format_str[idx] == '\\' and idx + 1 < len(format_str) and format_str[idx+1] == 'n'and (idx==0 or (idx-1>=0 and format_str[idx-1] != '\\')):
                            idx_list.append(i)

                    if idx_list:
                        self.bug_accumulator.append(
                            BugInstance('VA_FORMAT_STRING_USES_NEWLINE', Priorities.EXP_PRIORITY,
                                        patch.name, hunk.lines[i].lineno[1],
                                        'If java/util/Formatter class, java/io/PrintStream class or java/io/Writer class was used,'
                                        'format string should use %n rather than \\n.'
                                        'Otherwise, ignore this bug.')
                        )


