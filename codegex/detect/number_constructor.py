import regex

from codegex.models.bug_instance import BugInstance
from codegex.models.detectors import Detector, get_exact_lineno
from codegex.models.priorities import *
from codegex.utils.utils import get_string_ranges, in_range, simple_str_to_int


class NumberCTORDetector(Detector):
    def __init__(self):
        Detector.__init__(self)
        self.pattern = regex.compile(
            r'\bnew\s+(?:Integer|Long|Short|Byte|Character)\s*(?P<aux1>\(((?:[^()]++|(?&aux1))*)\))')

    def match(self, context):
        line_content = context.cur_line.content
        if 'new' in line_content and any(key in line_content for key in ('Integer', 'Long', 'Short', 'Byte', 'Character')):
            m = self.pattern.search(line_content)
            if m and not in_range(m.start(0), get_string_ranges(line_content)):
                int_val = simple_str_to_int(m.group(2).strip('"'))
                priority = MEDIUM_PRIORITY
                if int_val is not None and (int_val > -128 or int_val > 127):
                    priority = LOW_PRIORITY

                self.bug_accumulator.append(
                    BugInstance('DM_NUMBER_CTOR', priority, context.cur_patch.name,
                                get_exact_lineno(m.end(0), context.cur_line)[1],
                                'Method invokes inefficient Number constructor; use static valueOf instead',
                                sha=context.cur_patch.sha, line_content=context.cur_line.content)
                )


class FPNumberCTORDetector(Detector):
    def __init__(self):
        Detector.__init__(self)
        self.pattern = regex.compile(r'\bnew\s+(?:Double|Float)\s*(?P<aux1>\((?:[^()]++|(?&aux1))*\))')

    def match(self, context):
        line_content = context.cur_line.content
        if 'new' in line_content and any(key in line_content for key in ('Double', 'Float')):
            m = self.pattern.search(line_content)
            if m and not in_range(m.start(0), get_string_ranges(line_content)):
                self.bug_accumulator.append(
                    BugInstance(
                        'DM_FP_NUMBER_CTOR', LOW_PRIORITY, context.cur_patch.name,
                        get_exact_lineno(m.end(0), context.cur_line)[1],
                        'Method invokes inefficient floating-point Number constructor; use static valueOf instead',
                        sha=context.cur_patch.sha, line_content=context.cur_line.content)
                )