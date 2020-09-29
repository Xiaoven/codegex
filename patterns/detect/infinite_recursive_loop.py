import re

from patterns.detectors import ParentDetector, SubDetector
from patterns.bug_instance import BugInstance
import patterns.priorities as Priorities


class InfiniteRecursiveLoop(ParentDetector):
    def __init__(self):
        ParentDetector.__init__(self, [
            CollectionAddItselfSubDetector()
        ])


class CollectionAddItselfSubDetector(SubDetector):
    def __init__(self):
        self.pattern = re.compile(r'(.*)\.add\((.*)\)')
        SubDetector.__init__(self)

    def match(self, linecontent: str, filename: str, lineno: int):
        m = self.pattern.search(linecontent)
        if m:
            g = m.groups()
            assert len(g) == 2
            obj = g[0].strip()
            arg = g[1].strip()
            if obj == arg:
                self.bug_accumulator.append(
                    BugInstance('IL_CONTAINER_ADDED_TO_ITSELF', Priorities.HIGH_PRIORITY, filename,
                                lineno,
                                'A collection is added to itself')
                )
