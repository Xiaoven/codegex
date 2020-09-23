import re

from patterns.detectors import Detector

from patterns.bug_instance import BugInstance

import patterns.priorities as Priorities

from patterns.utils import is_comment


class StcalStaticSimpleDateFormatInstance(Detector):
    def __init__(self):
        self.regexp = re.compile('static\s*.*\s*(SimpleDateFormat|DateFormat|MyOwnDateFormat)')
    
    def _visit_patch(self, patch):
        for hunk in patch:
            for i in range(len(hunk.lines)):
                if i in hunk.dellines:
                    continue

                line_content = hunk.lines[i].content
                if i in hunk.addlines:
                    line_content = line_content[1:]  # remove "+"

                   
                if is_comment(line_content):
                    continue
                
                match = self.regexp.search(line_content)
                if match:
                    confidence = Priorities.NORMAL_PRIORITY
                    self.bug_accumulator.append(BugInstance('STCAL_STATIC_SIMPLE_DATE_FORMAT_INSTANCE', confidence,patch.name, hunk.lines[i].lineno[1],'Static DateFormat'))

