import re

from patterns.detectors import Detector
from patterns.bug_instance import BugInstance
import patterns.priorities as Priorities
from patterns.utils import is_comment


class AMCREATESEMPTYZIPFILEENTRY(Detector):
    def __init__(self):
        self.pattern1 = re.compile('(\w*)\.putNextEntry\(')
        self.pattern2 = re.compile('(\w*)\.closeEntry\(')

    def _visit_patch(self, patch):
        for hunk in patch:
            putNext = False
            for i in range(len(hunk.lines)):
                if i in hunk.dellines:
                    continue

                line_content = hunk.lines[i].content
                if i in hunk.addlines:
                    line_content = line_content[1:]  # remove "+"

                if is_comment(line_content):
                    continue

                match1 = self.pattern1.search(line_content)
                if match1:
                    putNext = True
                    continue

                match2 = self.pattern2.search(line_content)
                if match2 and putNext:
                    confidence = Priorities.NORMAL_PRIORITY
                    self.bug_accumulator.append(BugInstance('AM_CREATES_EMPTY_ZIP_FILE_ENTRY', confidence,
                                                            patch.name, hunk.lines[i].lineno[1],
                                                            'Creates an empty zip file entry'))
                putNext = False
