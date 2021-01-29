import regex

from patterns.models import priorities
from patterns.models.bug_instance import BugInstance
from patterns.models.detectors import Detector


class EqualsClassNameDetector(Detector):
    def __init__(self):
        self.pattern = regex.compile(r'\b((?:[\w\.$"]|(?:\(\s*\)))+)\s*\.\s*equals(?P<aux1>\(((?:[^()]++|(?&aux1))*)\))')
        Detector.__init__(self)

    def match(self, context):
        line_content = context.cur_line.content
        if not all(key in line_content for key in ('equals', 'getClass', 'getName')):
            return

        its = self.pattern.finditer(line_content)
        for m in its:
            g = m.groups()
            before_equals = g[0]
            after_equals = g[-1].strip()

            comparing_class_name = False
            if before_equals == 'Objects' and ',' in after_equals:
                elements = after_equals.split(',')
                for elem in elements:
                    if elem.replace(' ', '').endswith('getClass().getName()'):
                        comparing_class_name = True
                        break
            else:
                if before_equals.replace(' ', '').endswith('getClass().getName()'):
                    comparing_class_name = True
                elif after_equals.replace(' ', '').endswith('getClass().getName()'):
                    comparing_class_name = True

            if comparing_class_name:
                self.bug_accumulator.append(
                    BugInstance('EQ_COMPARING_CLASS_NAMES', priorities.MEDIUM_PRIORITY, context.cur_patch.name,
                                context.cur_line.lineno[1],
                                'Equals method compares class names rather than class objects'))
