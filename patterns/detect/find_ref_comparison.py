import regex

from patterns.detectors import ParentDetector, SubDetector
from patterns.bug_instance import BugInstance
import patterns.priorities as Priorities


class FindRefComparison(ParentDetector):
    def __init__(self):
        ParentDetector.__init__(self, [
            EqualitySubDetector(),
            CalToNullSubDetector()
        ])


class EqualitySubDetector(SubDetector):
    def __init__(self):
        self.p = regex.compile(
            r'((?:(?P<aux1>\((?:[^()]++|(?&aux1))*\))|[\w."])++)\s*[!=]=\s*((?:(?&aux1)|[\w."])+)')
        self.bool_objs = ('Boolean.TRUE', 'Boolean.FALSE')
        SubDetector.__init__(self)

    def match(self, linecontent: str, filename: str, lineno: int):
        m = self.p.search(linecontent)
        if m:
            op_1 = m.groups()[0]  # m.groups()[1] is the result of named pattern
            op_2 = m.groups()[2]

            if op_1 in self.bool_objs or op_2 in self.bool_objs:
                self.bug_accumulator.append(
                    BugInstance('RC_REF_COMPARISON_BAD_PRACTICE_BOOLEAN', Priorities.NORMAL_PRIORITY,
                                filename, lineno,
                                "Suspicious reference comparison of Boolean values")
                )
            else:
                if op_2.startswith('"'):
                    op_1, op_2 = op_2, op_1
                elif not op_1.startswith('"'):
                    return  # both op_1 and op_2 are not a string

                # now op_1 is a string with double quotes
                if op_2.startswith('"') or op_2.startswith('String.intern'):
                    return
                else:
                    self.bug_accumulator.append(
                        BugInstance('ES_COMPARING_STRINGS_WITH_EQ', Priorities.NORMAL_PRIORITY,
                                    filename, lineno,
                                    "Suspicious reference comparison of Boolean values")
                    )


class CalToNullSubDetector(SubDetector):
    def __init__(self):
        self.p = regex.compile(
            r'(.*)\.equals\s*\(\s*null\s*\)')
        SubDetector.__init__(self)

    def match(self, linecontent: str, filename: str, lineno: int):
        m = self.p.search(linecontent)
        if m:
            self.bug_accumulator.append(
                BugInstance('EC_NULL_ARG', Priorities.NORMAL_PRIORITY,
                            filename, lineno,
                            "Call to equals(null)")
            )
