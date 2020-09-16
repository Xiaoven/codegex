import re

from patterns.detectors import Detector
from patterns.bug_instance import BugInstance
import patterns.priorities as Priorities
from patterns.utils import is_comment


class EmptyZipFileEntry(Detector):
    def __init__(self):
        self.pattern1 = re.compile('\.putNextEntry\(')
        self.pattern2 = re.compile('\.closeEntry\(\s*\)')

    def _visit_patch(self, patch):
        for hunk in patch:
            putNext = False
            for i in range(len(hunk.lines)):
                if i in hunk.dellines:
                    continue

                line_content = hunk.lines[i].content
                if i in hunk.addlines:
                    line_content = line_content[1:]  # remove "+"

                if (not line_content.strip()) or is_comment(line_content):
                    continue

                if not putNext:
                    m = self.pattern1.search(line_content)
                    if m:
                        putNext = True
                        continue

                if putNext:
                    m = self.pattern2.search(line_content)
                    if m:
                        self.bug_accumulator.append(BugInstance('AM_CREATES_EMPTY_ZIP_FILE_ENTRY', Priorities.NORMAL_PRIORITY,
                                                                patch.name, hunk.lines[i].lineno[1],
                                                                'Creates an empty zip file entry'))

                putNext = False
