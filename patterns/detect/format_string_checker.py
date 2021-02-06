import regex

from patterns.models.detectors import Detector
from patterns.models.bug_instance import BugInstance
from patterns.models import priorities


class NewLineDetector(Detector):
    def __init__(self):
        self.pre_part = regex.compile(r'(\b\w[\w.]*)\s*\.\s*(format|printf|\w*fmt)\s*\(')
        self.params_part = regex.compile(r'(?P<aux>\(((?:[^()]++|(?&aux))*)\))')
        self.var_def_regex = regex.compile(r'\b(Formatter|PrintStream|\w*Writer|\w*Logger)\s+(\w+)\s*[;=]')
        self.patch, self.interesting_vars = None, dict()
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
                        type_name = self._local_search(obj_name, context)
                        if type_name:
                            priority = priorities.MEDIUM_PRIORITY

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

    def _local_search(self, var_name: str, context):
        # check if patch is updated
        if context.cur_patch != self.patch:
            self.patch = context.cur_patch
            self._init_interesting_vars()

        # check if the var_name is in interesting variable list
        if var_name in self.interesting_vars:
            return self.interesting_vars[var_name]

        return None

    def _init_interesting_vars(self):
        self.interesting_vars.clear()
        if not self.patch:
            return
        for hunk in self.patch:
            for line in hunk:
                if line.prefix == '-':
                    continue
                if any(key in line.content for key in ('Formatter', 'PrintStream', 'Writer', 'Logger')):
                    m = self.var_def_regex.search(line.content)
                    if m:
                        type_name = m.groups()[0]
                        var_name = m.groups()[1]
                        self.interesting_vars[var_name] = type_name

