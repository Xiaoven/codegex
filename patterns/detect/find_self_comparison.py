import regex

from patterns.models.bug_instance import BugInstance
from patterns.models.detectors import Detector
import patterns.models.priorities as Priorities


class CheckForSelfComputation(Detector):
    def __init__(self):
        self.pattern = regex.compile(r'(\b\w[\w.]*(?P<aux1>\((?:[^()]++|(?&aux1))*\))*+)\s*([|^&-])\s*\1[^.\w$]')
        Detector.__init__(self)

    def match(self, linecontent: str, filename: str, lineno: int, **kwargs):
        if not any(op in linecontent for op in ('&', '|', '^', '-')):
            return

        its = self.pattern.finditer(linecontent)
        for m in its:
            self.bug_accumulator.append(
                BugInstance('SA_SELF_COMPUTATION', Priorities.MEDIUM_PRIORITY, filename, lineno,
                            'Nonsensical self computation involving a variable or field')
            )


class CheckForSelfComparison(Detector):
    def __init__(self):
        self.pattern_1 = regex.compile(r'(\b\w[\w.]*(?P<aux1>\((?:[^()]++|(?&aux1))*\))*+)\s*([><=!]+)\s*\1[^.\w$]')
        self.pattern_2 = regex.compile(
            r'\b((?:[\w\.$"]|(?:\(\s*\)))+)\s*\.\s*(?:equals|compareTo|endsWith|startsWith|contains|equalsIgnoreCase|compareToIgnoreCase)(?P<aux1>\(((?:[^()]++|(?&aux1))*)\))')
        Detector.__init__(self)

    def match(self, linecontent: str, filename: str, lineno: int, **kwargs):
        hit = False
        if any(op in linecontent for op in ('>', '<', '>=', '<=', '==', '!=')):
            its = self.pattern_1.finditer(linecontent)
            for m in its:
                relation_op = m.groups()[-1]
                if relation_op in ('>', '<', '>=', '<=', '==', '!='):
                    hit = True
                    break

        if not hit and any(method in linecontent for method in ('equals', 'compareTo', 'endsWith', 'startsWith', 'contains',
                                                    'equalsIgnoreCase', 'compareToIgnoreCase')):
            its = self.pattern_2.finditer(linecontent)
            for m in its:
                g = m.groups()
                before_method = g[0]
                after_method = g[-1].strip()

                if before_method == after_method:
                    hit = True
                    break
                else:
                    elements = after_method.split(',')
                    if len(elements) == 2 and elements[0] == elements[2]:
                        hit = True
                        break

        if hit:
            self.bug_accumulator.append(
                BugInstance('SA_SELF_COMPARISON', Priorities.MEDIUM_PRIORITY, filename, lineno,
                            'Self comparison of value or field with itself')
            )

