import regex

from patterns.models.bug_instance import BugInstance
from patterns.models.detectors import Detector
import patterns.models.priorities as Priorities


class CheckForSelfComputation(Detector):
    def __init__(self):
        self.pattern = regex.compile(r'(\b\w[\w.]*(?P<aux1>\((?:[^()]++|(?&aux1))*\))*)\s*([|^&-])\s*([\w.]+(?&aux1)*)')
        Detector.__init__(self)

    def match(self, context):
        line_content = context.cur_line.content
        if all(op not in line_content for op in ('&', '|', '^', '-')):
            return

        its = self.pattern.finditer(line_content)
        for m in its:
            g = m.groups()
            obj_1 = g[0]
            op = g[2]
            obj_2 = g[3]
            if obj_1 == obj_2 and op in ('&', '|', '^', '-'):
                self.bug_accumulator.append(
                    BugInstance('SA_SELF_COMPUTATION', Priorities.MEDIUM_PRIORITY, context.cur_patch.name,
                                context.cur_line.lineno[1],
                                'Nonsensical self computation involving a variable or field')
                )
                return


class CheckForSelfComparison(Detector):
    def __init__(self):
        self.pattern_1 = regex.compile(
            r'(\b\w[\w.]*(?P<aux1>\((?:[^()]++|(?&aux1))*\))*)\s*([><=!]+)\s*([\w.]+(?&aux1)*)')
        self.pattern_2 = regex.compile(
            r'\b((?:[\w\.$"]|(?:\(\s*\)))+)\s*\.\s*(?:equals|compareTo|endsWith|startsWith|contains|equalsIgnoreCase|compareToIgnoreCase)(?P<aux1>\(((?:[^()]++|(?&aux1))*)\))')
        Detector.__init__(self)

    def match(self, context):
        line_content = context.cur_line.content
        hit = False
        if any(op in line_content for op in ('>', '<', '>=', '<=', '==', '!=')):
            its = self.pattern_1.finditer(line_content)
            for m in its:
                g = m.groups()
                obj_1 = g[0]
                relation_op = g[2]
                obj_2 = g[3]
                if obj_1 == obj_2 and relation_op in ('>', '<', '>=', '<=', '==', '!='):
                    hit = True
                    break

        if not hit and any(method in line_content for method in ('equals', 'compareTo', 'endsWith', 'startsWith',
                                                                'contains', 'equalsIgnoreCase', 'compareToIgnoreCase')):
            its = self.pattern_2.finditer(line_content)
            for m in its:
                g = m.groups()
                before_method = g[0]
                after_method = g[-1].strip()

                if before_method == after_method:
                    hit = True
                    break
                else:
                    elements = after_method.split(',')

                    if len(elements) == 2 and elements[0] == elements[1]:
                        hit = True
                        break

        if hit:
            self.bug_accumulator.append(
                BugInstance('SA_SELF_COMPARISON', Priorities.MEDIUM_PRIORITY, context.cur_patch.name,
                            context.cur_line.lineno[1],
                            'Self comparison of value or field with itself')
            )

