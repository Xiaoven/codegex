import regex

from patterns.models.detectors import Detector
from patterns.models.bug_instance import BugInstance
from patterns.models import priorities


class StaticDateFormatDetector(Detector):
    def __init__(self):
        self.p = regex.compile(
            r'^([\w\s]*?)\bstatic\s*(?:final)?\s+(DateFormat|SimpleDateFormat|Calendar|GregorianCalendar)\s+(\w+)\s*[;=]')
        Detector.__init__(self)

    def match(self, linecontent: str, filename: str, lineno: int, **kwargs):
        if not any(key in linecontent for key in ('DateFormat', 'Calendar')):
            return

        m = self.p.search(linecontent.strip())

        if m:
            groups = m.groups()
            access = groups[0].strip()
            if access and 'private' in access.split():
                return
            class_name = groups[1]
            field_name = groups[2]
            if class_name.endswith('DateFormat'):
                self.bug_accumulator.append(
                    BugInstance('STCAL_STATIC_SIMPLE_DATE_FORMAT_INSTANCE',
                                priorities.MEDIUM_PRIORITY, filename, lineno,
                                f"{field_name} is a static field of type java.text.DateFormat, which isn't thread safe"))
            else:
                self.bug_accumulator.append(
                    BugInstance('STCAL_STATIC_CALENDAR_INSTANCE',
                                priorities.MEDIUM_PRIORITY, filename, lineno,
                                f"{field_name} is a static field of type java.util.Calendar, which isn't thread safe"))
