import re

from patterns.detectors import Detector
from patterns.bug_instance import BugInstance
import patterns.priorities as Priorities
from patterns.utils import is_comment


class SerializableIdiom(Detector):
    def __init__(self):
        self.pattern = re.compile('\s+serialVersionUID(?!\w)')

    def _visit_patch(self, patch):
        for hunk in patch:
            for i in range(len(hunk.lines)):
                # detect all lines in the patch rather than the addition
                if i in hunk.dellines:
                    continue

                line_content = hunk.lines[i].content
                if i in hunk.addlines:
                    line_content = line_content[1:]  # remove "+"

                if is_comment(line_content):
                    continue

                line_content = line_content.strip()
                m = self.pattern.search(line_content)
                if m:
                    start_offset = m.start()
                    prefix = line_content[:start_offset]
                    prefixes = prefix.split()

                    if 'static' not in prefix:
                        self.bug_accumulator.append(
                            BugInstance('SE_NONSTATIC_SERIALVERSIONID', Priorities.NORMAL_PRIORITY, patch.name, hunk.lines[i].lineno[1],
                                        "serialVersionUID isn't static.")
                        )
                    if 'final' not in prefix:
                        self.bug_accumulator.append(
                            BugInstance('SE_NONFINAL_SERIALVERSIONID', Priorities.NORMAL_PRIORITY, patch.name, hunk.lines[i].lineno[1],
                                        "serialVersionUID isn't final.")
                        )
                    if 'long' not in prefix:
                        self.bug_accumulator.append(
                            BugInstance('SE_NONLONG_SERIALVERSIONID', Priorities.LOW_PRIORITY, patch.name,
                                        hunk.lines[i].lineno[1],
                                        "serialVersionUID isn't long.")
                        )


