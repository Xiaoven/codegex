import regex

from patterns.models.bug_instance import BugInstance
from patterns.models.detectors import Detector, get_exact_lineno
from patterns.models.priorities import *
from utils import in_range, get_string_ranges


class VolatileArrayDetector(Detector):
    def __init__(self):
        Detector.__init__(self)
        self.pattern = regex.compile(r'\bvolatile\s+\w+\s*(?P<gen><(?:[^<>]++|(?&gen))*>)?\s*\[\s*\]\s+\w+\s*[;=]')

    def match(self, context):
        line_content = context.cur_line.content
        if all(key in line_content for key in ('volatile', '[', ']')):
            m = self.pattern.search(line_content)
            if m and not in_range(m.start(0), get_string_ranges(line_content)):
                self.bug_accumulator.append(
                    BugInstance('VO_VOLATILE_REFERENCE_TO_ARRAY', LOW_PRIORITY,
                                context.cur_patch.name, get_exact_lineno(m.end(0), context.cur_line)[1],
                                "A volatile reference to an array doesn’t treat the array elements as volatile",
                                sha=context.cur_patch.sha, line_content=context.cur_line.content)
                )
