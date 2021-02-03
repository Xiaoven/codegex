import regex

from patterns.models import priorities
from patterns.models.bug_instance import BugInstance
from patterns.models.detectors import Detector


class BooleanAssignmentDetector(Detector):
    def __init__(self):
        self.extract = regex.compile(r'\b(?:if|while)\s*(?P<aux>\(((?:[^()]++|(?&aux))*)\))')
        self.assignment = regex.compile(r'\b[\w$]+\s*=\s*(?:true|false)\b')
        Detector.__init__(self)

    def match(self, context):
        line_content = context.cur_line.content
        if all(key not in line_content for key in ('if', 'while')) or \
                all(key not in line_content for key in ('true', 'false')) or '=' not in line_content:
            return

        m_1 = self.extract.search(line_content.strip())
        if m_1:
            conditions = m_1.groups()[1]
            m_2 = self.assignment.search(conditions)
            if m_2:
                self.bug_accumulator.append(
                    BugInstance('QBA_QUESTIONABLE_BOOLEAN_ASSIGNMENT', priorities.HIGH_PRIORITY,
                                context.cur_patch.name, context.cur_line.lineno[1],
                                'Method assigns boolean literal in boolean expression', sha=context.cur_patch.sha))
