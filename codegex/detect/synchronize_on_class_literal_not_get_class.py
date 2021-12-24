import regex

from codegex.models.bug_instance import BugInstance
from codegex.models.detectors import Detector, get_exact_lineno
from codegex.models.priorities import *
from codegex.utils.utils import in_range, get_string_ranges


class SynGetClassDetector(Detector):
    def __init__(self):
        Detector.__init__(self)
        self.pattern = regex.compile(r'\bsynchronized\s*\(\s*(?:this\s*\.\s*)?getClass\s*\(\s*\)\s*\)')

    def match(self, context):
        line_content = context.cur_line.content
        if all(key in line_content for key in ('synchronized', 'getClass')):
            m = self.pattern.search(line_content)
            if m and not in_range(m.start(0), get_string_ranges(line_content)):
                self.bug_accumulator.append(
                    BugInstance('WL_USING_GETCLASS_RATHER_THAN_CLASS_LITERAL', LOW_PRIORITY,
                                context.cur_patch.name, get_exact_lineno(m.end(0), context.cur_line)[1],
                                "Synchronization on getClass rather than class literal",
                                sha=context.cur_patch.sha, line_content=context.cur_line.content)
                )
