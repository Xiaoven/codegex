import regex

from patterns.models.detectors import Detector
from patterns.models.bug_instance import BugInstance
from patterns.models import priorities


class NewLineDetector(Detector):
    # def __init__(self):
    #     super().__init__()
    #     self.p = re.compile(r'(?:(?:String\.format)|printf)\([\w.\s()]*,?\s*"([^"]*)"\s*')
    #
    # def match(self, context):
    #     line_content = context.cur_line.content
    #     line_no = context.cur_line.lineno[1]
    #     m = self.p.search(line_content.strip())
    #     if m:
    #         format_str = m.groups()[0]
    #
    #         if '\\n' in format_str:
    #             if hasattr(context.cur_line, 'get_exact_lineno'):
    #                 tmp = context.cur_line.get_exact_lineno(format_str)
    #                 if tmp:
    #                     line_no = tmp[1]
    #
    #             self.bug_accumulator.append(
    #                 BugInstance('VA_FORMAT_STRING_USES_NEWLINE', priorities.MEDIUM_PRIORITY,
    #                             context.cur_patch.name, line_no,
    #                             'Format string should use %n rather than \\n', sha=context.cur_patch.sha)
    #             )

    def __init__(self):
        self.pre_part = regex.compile(r'(\b\w[\w.]*)\s*\.\s*(format|printf|\w*fmt)\s*\(')
        self.params_part = regex.compile(r'(?P<aux>\(((?:[^()]++|(?&aux))*)\))')
        Detector.__init__(self)

    def match(self, context):
        strip_line = context.cur_line.content.strip()
        # if the line contains strings with double quote and key words
        if any(key in strip_line for key in ('format', 'printf', 'fmt')):
            m = self.pre_part.search(strip_line)
            if m:
                g = m.groups()
                obj_name = g[0]
                method_name = g[1]

                m_2 = self.params_part.match(strip_line[m.end(0) - 1:])
                if m_2:
                    params = m_2.groups()[1]
                else:
                    params = strip_line[m.end(0):]
                # Check if strings within params contains '\\n' which only occurs in a string
                if '\\n' in params:
                    # Adjust priority
                    priority = priorities.LOW_PRIORITY
                    obj_name_lower = obj_name.lower()

                    if method_name == 'format' and (obj_name == 'String' or obj_name_lower.endswith('formatter')
                                                    or obj_name_lower.endswith('writer')):
                        priority = priorities.MEDIUM_PRIORITY
                    elif method_name == 'printf' and (obj_name == 'System.out.' or obj_name_lower.endswith('writer')):
                        priority = priorities.MEDIUM_PRIORITY
                    elif method_name == 'fmt' and obj_name_lower.endswith('logger'):
                        priority = priorities.MEDIUM_PRIORITY
                    else:
                        pass  # local search

                    # get exact line number
                    line_no = context.cur_line.lineno[1]
                    if hasattr(context.cur_line, 'get_exact_lineno'):
                        tmp = context.cur_line.get_exact_lineno('\\n')
                        if tmp:
                            line_no = tmp[1]



                    self.bug_accumulator.append(
                        BugInstance('VA_FORMAT_STRING_USES_NEWLINE', priority,
                                    context.cur_patch.name, line_no,
                                    'Format string should use %n rather than \\n', sha=context.cur_patch.sha)
                    )
                    return
