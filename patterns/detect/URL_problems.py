import regex

from patterns.models.bug_instance import BugInstance
from patterns.models.detectors import Detector, get_exact_lineno
from patterns.models.priorities import *
from utils import in_range, get_string_ranges


class URLCollectionDetector(Detector):
    def __init__(self):
        Detector.__init__(self)
        self.pattern = regex.compile(
            r'(?:(?:(?:Hash)?(Set|Map))|HashTable)\s*<\s*URL(?:\s*,\s*\w+(?P<gen><(?:[^<>]++|(?&gen))*>))?\s*\>')

    def match(self, context):
        line_content = context.cur_line.content
        if 'URL' in line_content and any(key in line_content for key in ('Map', 'Set')):
            m = self.pattern.search(line_content)
            if m and not in_range(m.start(0), get_string_ranges(line_content)):
                self.bug_accumulator.append(
                    BugInstance('DMI_COLLECTION_OF_URLS', LOW_PRIORITY,
                                context.cur_patch.name, get_exact_lineno(m.end(0), context.cur_line)[1],
                                "Maps and sets of URLs can be performance hogs",
                                sha=context.cur_patch.sha, line_content=context.cur_line.content)
                )
