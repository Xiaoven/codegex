import regex

from patterns.models import priorities
from patterns.models.bug_instance import BugInstance
from patterns.models.detectors import Detector


class BooleanAssignmentDetector(Detector):
    def __init__(self):
        self.extract = regex.compile(r'\b(?:if|while)\s*(?P<aux>\(((?:[^()]++|(?&aux))*)\))')
        self.assignment = regex.compile(r'\b[\w$]+\s*=\s*(?:true|false)\b')
        Detector.__init__(self)

    def match(self, linecontent: str, filename: str, lineno: int, **kwargs):
        if all(key not in linecontent for key in ('if', 'while')) or \
                all(key not in linecontent for key in ('true', 'false')) or '=' not in linecontent:
            return

        m_1 = self.extract.search(linecontent.strip())
        if m_1:
            conditions = m_1.groups()[1]
            m_2 = self.assignment.search(conditions)
            if m_2:
                self.bug_accumulator.append(
                    BugInstance('QBA_QUESTIONABLE_BOOLEAN_ASSIGNMENT', priorities.HIGH_PRIORITY,
                                filename, lineno, 'Method assigns boolean literal in boolean expression'))
