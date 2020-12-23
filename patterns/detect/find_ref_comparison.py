import regex

from patterns.detectors import Detector
from patterns.bug_instance import BugInstance
import patterns.priorities as Priorities


def is_str_with_quotes(s:str):
    s = s.strip()
    if s.startswith('"') and s.endswith('"'):
        return True
    return False


class EqualityDetector(Detector):
    def __init__(self):
        self.p = regex.compile(
            r'((?:(?P<aux1>\((?:[^()]++|(?&aux1))*\))|[\w."])++)\s*[!=]=\s*((?:(?&aux1)|[\w."])+)')
        self.bool_objs = ('Boolean.TRUE', 'Boolean.FALSE')
        Detector.__init__(self)

    def match(self, linecontent: str, filename: str, lineno: int, get_exact_lineno=None):
        # Leading [\w."] may cause to catastrophic backtracking,
        # and it is a little complicate to rewrite regex with word boundary `\b`
        # therefore, use the following condition to speed up.
        if not any(op in linecontent for op in ['==', '!=']):
            return

        m = self.p.search(linecontent.strip())
        if m:
            op_1 = m.groups()[0]  # m.groups()[1] is the result of named pattern
            op_2 = m.groups()[2]

            if op_1 in self.bool_objs or op_2 in self.bool_objs:
                self.bug_accumulator.append(
                    BugInstance('RC_REF_COMPARISON_BAD_PRACTICE_BOOLEAN', Priorities.MEDIUM_PRIORITY,
                                filename, lineno,
                                "Suspicious reference comparison of Boolean values")
                )
            else:
                if is_str_with_quotes(op_2):
                    op_1, op_2 = op_2, op_1
                elif not is_str_with_quotes(op_1):
                    return  # both op_1 and op_2 are not a string

                # now op_1 is a string with double quotes
                if is_str_with_quotes(op_2) or op_2.startswith('String.intern'):
                    return
                else:
                    self.bug_accumulator.append(
                        BugInstance('ES_COMPARING_STRINGS_WITH_EQ', Priorities.MEDIUM_PRIORITY,
                                    filename, lineno,
                                    "Suspicious reference comparison of String objects")
                    )


class CalToNullDetector(Detector):
    def __init__(self):
        self.p = regex.compile(
            r'\.equals\s*\(\s*null\s*\)')
        Detector.__init__(self)

    def match(self, linecontent: str, filename: str, lineno: int, get_exact_lineno=None):
        m = self.p.search(linecontent.strip())
        if m:
            self.bug_accumulator.append(
                BugInstance('EC_NULL_ARG', Priorities.MEDIUM_PRIORITY,
                            filename, lineno,
                            "Call to equals(null)")
            )
