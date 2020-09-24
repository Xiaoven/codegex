import regex

from patterns.detectors import ParentDetector, SubDetector
from patterns.bug_instance import BugInstance
import patterns.priorities as Priorities


class StaticCalendarDetector(ParentDetector):
    def __init__(self):
        ParentDetector.__init__(self, [
            StaticDateFormatSubDetector()
        ])


class StaticDateFormatSubDetector(SubDetector):
    def __init__(self):
        self.p = regex.compile(r'(\w*\s*)static\s+(?:final){0,1}\s*(?:java\.text\.){0,1}(DateFormat|SimpleDateFormat)\s+(\w*)')
        SubDetector.__init__(self)

    def match(self, linecontent: str, filename: str, lineno: int):
        m = self.p.search(linecontent)

        if m:
            groups = m.groups()
            assert len(groups) == 3
            access = groups[0]
            if access and 'private' in access.split():
                return
            class_name = groups[1]
            field_name = groups[2]
            if class_name.endswith('DateFormat'): # may extend with Calendar in the future
                self.bug_accumulator.append(
                    BugInstance('STCAL_STATIC_SIMPLE_DATE_FORMAT_INSTANCE',
                                Priorities.NORMAL_PRIORITY, filename, lineno,
                                f"{field_name} is a static field of type java.text.DateFormat, which isn't thread safe"))
