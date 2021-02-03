import regex

from patterns.models.detectors import Detector
from patterns.models.bug_instance import BugInstance
from patterns.models import priorities


def is_str_with_quotes(s: str):
    s = s.strip()
    if len(s) > 1 and s.startswith('"') and s.endswith('"'):
        return True
    return False


class EqualityDetector(Detector):
    def __init__(self):
        self.p = regex.compile(
            r'((?:(?P<aux1>\((?:[^()]++|(?&aux1))*\))|[\w.$"])++)\s*[!=]=\s*((?:(?&aux1)|[\w.$"])+)')
        self.bool_objs = ('Boolean.TRUE', 'Boolean.FALSE')
        Detector.__init__(self)

    def match(self, context):
        line_content = context.cur_line.content
        # Leading [\w."] may cause to catastrophic backtracking,
        # and it is a little complicate to rewrite regex with word boundary `\b`
        # therefore, use the following condition to speed up.
        if not any(op in line_content for op in ['==', '!=']):
            return

        its = self.p.finditer(line_content.strip())
        for m in its:
            op_1 = m.groups()[0]  # m.groups()[1] is the result of named pattern
            op_2 = m.groups()[2]

            if op_1 in self.bool_objs or op_2 in self.bool_objs:
                self.bug_accumulator.append(
                    BugInstance('RC_REF_COMPARISON_BAD_PRACTICE_BOOLEAN', priorities.MEDIUM_PRIORITY,
                                context.cur_patch.name, context.cur_line.lineno[1],
                                "Suspicious reference comparison of Boolean values", sha=context.cur_patch.sha)
                )
                break
            else:
                if is_str_with_quotes(op_2):
                    op_1, op_2 = op_2, op_1
                elif not is_str_with_quotes(op_1):
                    continue  # both op_1 and op_2 are not a string

                # now op_1 is a string with double quotes
                if is_str_with_quotes(op_2) or op_2.startswith('String.intern'):
                    continue
                else:
                    self.bug_accumulator.append(
                        BugInstance('ES_COMPARING_STRINGS_WITH_EQ', priorities.MEDIUM_PRIORITY,
                                    context.cur_patch.name, context.cur_line.lineno[1],
                                    "Suspicious reference comparison of String objects", sha=context.cur_patch.sha))
                    break


class CallToNullDetector(Detector):
    def __init__(self):
        self.p = regex.compile(
            r'\.equals\s*\(\s*null\s*\)')
        Detector.__init__(self)

    def match(self, context):
        line_content = context.cur_line.content
        its = self.p.finditer(line_content.strip())
        for m in its:
            self.bug_accumulator.append(
                BugInstance('EC_NULL_ARG', priorities.MEDIUM_PRIORITY,
                            context.cur_patch.name, context.cur_line.lineno[1],
                            "Call to equals(null)", sha=context.cur_patch.sha)
            )
            return
