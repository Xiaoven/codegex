import regex

from patterns.models.detectors import Detector
from patterns.models.bug_instance import BugInstance
from patterns.models import priorities


class StaticDateFormatDetector(Detector):
    def __init__(self):
        self.p = regex.compile(
            r'^([\w\s]*?)\bstatic\s*(?:final)?\s+(DateFormat|SimpleDateFormat|Calendar|GregorianCalendar)\s+(\w+)\s*[;=]')
        Detector.__init__(self)

    def match(self, context):
        line_content = context.cur_line.content
        if not any(key in line_content for key in ('DateFormat', 'Calendar')):
            return

        m = self.p.search(line_content.strip())

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
                                priorities.MEDIUM_PRIORITY, context.cur_patch.name, context.cur_line.lineno[1],
                                f"{field_name} is a static field of type java.text.DateFormat, which isn't thread safe"))
            else:
                self.bug_accumulator.append(
                    BugInstance('STCAL_STATIC_CALENDAR_INSTANCE',
                                priorities.MEDIUM_PRIORITY, context.cur_patch.name, context.cur_line.lineno[1],
                                f"{field_name} is a static field of type java.util.Calendar, which isn't thread safe"))
