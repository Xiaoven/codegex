import regex

from patterns.detectors import Detector
from patterns.bug_instance import BugInstance
import patterns.priorities as Priorities


class SuspiciousCollectionMethodDetector(Detector):
    def __init__(self):
        self.pattern = regex.compile(
            r'(\b\w[\w.]*(?P<aux1>\((?:[^()]++|(?&aux1))*\))*+)\s*\.\s*((?:remove|contains|retain)(?:All)?)\s*\(\s*\1\s*\)')
        Detector.__init__(self)

    def match(self, linecontent: str, filename: str, lineno: int, get_exact_lineno=None):
        if not any(method in linecontent for method in ['remove', 'contains', 'retain']):
            return

        m = self.pattern.search(linecontent.strip())

        if m:
            g = m.groups()
            pattern_type, description, priority = None, None, None
            if g[-1] == 'removeAll':
                pattern_type = 'DMI_USING_REMOVEALL_TO_CLEAR_COLLECTION'
                description = 'removeAll used to clear a collection'
                priority = Priorities.MEDIUM_PRIORITY
            elif g[-1] in ['containsAll', 'retainAll']:
                pattern_type = 'DMI_VACUOUS_SELF_COLLECTION_CALL'
                description = 'Vacuous call to collections'
                priority = Priorities.MEDIUM_PRIORITY
            elif g[-1] in ['contains', 'remove']:
                pattern_type = 'DMI_COLLECTIONS_SHOULD_NOT_CONTAIN_THEMSELVES'
                description = 'Collections should not contain themselves'
                priority = Priorities.HIGH_PRIORITY

            if pattern_type:
                self.bug_accumulator.append(
                    BugInstance(pattern_type, priority, filename, lineno,
                                description)
                )
