import regex

from patterns.models.bug_instance import BugInstance
from patterns.models.detectors import Detector
import patterns.models.priorities as Priorities
from utils import get_generic_type_ranges, get_string_ranges, in_range


class CheckForSelfComputation(Detector):
    def __init__(self):
        self.pattern = regex.compile(
            r'([|^&-*/%]?)\s*(\b\w[\w.]*(?P<aux1>\((?:[^()]++|(?&aux1))*\))*)\s*([|^&-])\s*([\w.]+(?&aux1)*)\s*([|^&-*/%]?)')
        Detector.__init__(self)

        self._op_precedence_dict = {
            '*': 5, '/': 5, '%': 5,
            '-': 4,
            '&': 3, '^': 2, '|': 1,
        }

    def _is_precedent(self, op_1, op_2):
        assert all(op in self._op_precedence_dict for op in (op_1, op_2))
        return self._op_precedence_dict[op_1] > self._op_precedence_dict[op_2]

    def match(self, context):
        line_content = context.cur_line.content
        if all(op not in line_content for op in ('&', '|', '^', '-')):
            return

        string_ranges = get_string_ranges(line_content)

        its = self.pattern.finditer(line_content)
        for m in its:
            g = m.groups()
            op_front = g[0]
            obj_1 = g[1]
            op = g[3]
            op_offset = m.start(4)
            obj_2 = g[4]
            op_behind = g[5]
            if obj_1 == obj_2 and op in ('&', '|', '^', '-') and not in_range(op_offset, string_ranges):
                # Check operator precedence to avoid false positives
                if op_front in self._op_precedence_dict and self._is_precedent(op_front, op):
                    continue
                if op_behind in self._op_precedence_dict and self._is_precedent(op_behind, op):
                    continue
                self.bug_accumulator.append(
                    BugInstance('SA_SELF_COMPUTATION', Priorities.MEDIUM_PRIORITY, context.cur_patch.name,
                                context.cur_line.lineno[1],
                                'Nonsensical self computation involving a variable or field', sha=context.cur_patch.sha)
                )
                return


class CheckForSelfComparison(Detector):
    def __init__(self):
        self.pattern_1 = regex.compile(
            r'(\b\w[\w.]*(?P<aux1>\((?:[^()]++|(?&aux1))*\))*)\s*(==|!=|>=|<=|>|<)\s*([\w.]+(?&aux1)*)')
        self.pattern_2 = regex.compile(
            r'\b((?:[\w\.$"]|(?:\(\s*\)))+)\s*\.\s*(?:equals|compareTo|endsWith|startsWith|contains|equalsIgnoreCase|compareToIgnoreCase)(?P<aux1>\(((?:[^()]++|(?&aux1))*)\))')
        Detector.__init__(self)

    def match(self, context):
        line_content = context.cur_line.content
        string_ranges = get_string_ranges(line_content)

        hit = False
        if any(op in line_content for op in ('>', '<', '>=', '<=', '==', '!=')):
            generic_type_ranges = get_generic_type_ranges(line_content)
            its = self.pattern_1.finditer(line_content)
            for m in its:
                op_offset = m.start(3)  # the start offset of relation_op
                if in_range(op_offset, string_ranges):
                    continue
                g = m.groups()
                obj_1 = g[0]
                relation_op = g[2]
                obj_2 = g[3]
                if obj_1 == obj_2:
                    # check if in generic type range
                    if relation_op in ('<', '>') and in_range(op_offset, generic_type_ranges):
                        continue

                    hit = True
                    break

        if not hit and any(method in line_content for method in ('equals', 'compareTo', 'endsWith', 'startsWith',
                                                                 'contains', 'equalsIgnoreCase',
                                                                 'compareToIgnoreCase')):
            its = self.pattern_2.finditer(line_content)
            for m in its:
                op_offset = m.start()
                if in_range(op_offset, string_ranges):
                    continue
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
                            'Self comparison of value or field with itself', sha=context.cur_patch.sha)
            )
