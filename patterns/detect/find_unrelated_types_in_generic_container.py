import regex as re

from patterns.detectors import ParentDetector, SubDetector
from patterns.bug_instance import BugInstance
import patterns.priorities as Priorities


class FindUnrelatedTypesInGenericContainer(ParentDetector):
    def __init__(self):
        ParentDetector.__init__(self, [
            RemoveAllSubDetector(),
            VacuousSelfCallSubDetector(),
            NotContainThemselvesSubDetector()
        ])


class RemoveAllSubDetector(SubDetector):
    def __init__(self):
        self.pattern = re.compile(
            r'([\w_\.]+(?:(?P<aux1>\((?:[^()]++|(?&aux1))*\)))*+)\s*\.\s*removeAll\s*\(\s*\1\s*\)')
        SubDetector.__init__(self)

    def match(self, linecontent: str, filename: str, lineno: int, get_exact_lineno=None):
        m = self.pattern.search(linecontent)
        if m:
            self.bug_accumulator.append(
                BugInstance('DMI_USING_REMOVEALL_TO_CLEAR_COLLECTION', Priorities.NORMAL_PRIORITY, filename, lineno,
                            'removeAll used to clear a collection')
            )


class VacuousSelfCallSubDetector(SubDetector):
    def __init__(self):
        self.pattern = re.compile(
            r'([\w_\.]+(?:(?P<aux1>\((?:[^()]++|(?&aux1))*\)))*+)\s*\.\s*(?:contains|retain)All\s*\(\s*\1\s*\)')
        SubDetector.__init__(self)

    def match(self, linecontent: str, filename: str, lineno: int, get_exact_lineno=None):
        m = self.pattern.search(linecontent)
        if m:
            self.bug_accumulator.append(
                BugInstance('DMI_VACUOUS_SELF_COLLECTION_CALL', Priorities.NORMAL_PRIORITY, filename, lineno,
                            'Vacuous call to collections')
            )


class NotContainThemselvesSubDetector(SubDetector):
    def __init__(self):
        self.pattern = re.compile(
            r'([\w_\.]+(?:(?P<aux1>\((?:[^()]++|(?&aux1))*\)))*+)\s*\.\s*(?:contains|remove)\s*\(\s*\1\s*\)')
        SubDetector.__init__(self)

    def match(self, linecontent: str, filename: str, lineno: int, get_exact_lineno=None):
        m = self.pattern.search(linecontent)
        if m:
            self.bug_accumulator.append(
                BugInstance('DMI_COLLECTIONS_SHOULD_NOT_CONTAIN_THEMSELVES', Priorities.HIGH_PRIORITY, filename,
                            lineno,
                            'Collections should not contain themselves')
            )
