import re

from patterns.detectors import Detector
from patterns.bug_instance import BugInstance
import patterns.priorities as Priorities
from patterns.utils import is_comment


class FormatStringChecker(Detector):
    def __init__(self):
       self.p = re.compile('(?:(?:String\.format)|printf)\([\w\.\s\(\)]*,{0,1}\s*\"([^\"]*)\"\s*')

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
                if m:
                    format_str = m.groups()[0]
                    last_line = ''

                    if '\\n' in format_str:
                        self.bug_accumulator.append(
                            BugInstance('VA_FORMAT_STRING_USES_NEWLINE', Priorities.NORMAL_PRIORITY,
                                        patch.name, hunk.lines[i].lineno[1],
                                        'Format string should use %n rather than \\n')
                        )



