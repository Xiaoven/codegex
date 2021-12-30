import regex

from codegex.models.priorities import *
from codegex.models.bug_instance import BugInstance
from codegex.models.detectors import Detector, get_exact_lineno
import os

from codegex.utils.utils import in_range, get_string_ranges


class UselessSubstringDetector(Detector):
    def __init__(self):
        self.pattern = regex.compile(r'\.\s*substring\s*\(\s*0\s*\)')
        Detector.__init__(self)

    def match(self, context):
        line_content = context.cur_line.content
        m = self.pattern.search(line_content)
        if m:
            line_no = get_exact_lineno(m.end(0), context.cur_line)[1]
            self.bug_accumulator.append(
                BugInstance('DMI_USELESS_SUBSTRING', MEDIUM_PRIORITY, context.cur_patch.name, line_no,
                            'This code invokes substring(0) on a String, which returns the original value.',
                            sha=context.cur_patch.sha,
                            line_content=context.cur_line.content)
            )


def is_abs_filename(fn):
    if fn.startswith("/dev/"):
        return False
    if fn.startswith("/"):
        return True
    if fn.startswith("\\\\"):
        # UNC pathname like \\Server\share\...
        return True
    if len(fn) >= 2 and fn[1] == ':':
        drive_letter = fn[0]
        if ('A' <= drive_letter <= 'Z') or ('a' <= drive_letter <= 'z'):
            return True
    if os.path.isabs(fn):
        return True
    return False


class IsAbsoluteFileNameDetector(Detector):
    def __init__(self):
        self.pattern = regex.compile(
            r'\bnew\s+(?:File|RandomAccessFile|Paths|FileReader|FileWriter|FileInputStream|FileOutputStream|Formatter|JarFile|ZipFile|PrintStream|PrintWriter)\s*(?P<aux1>\((?:[^()]++|(?&aux1))*\))')
        self.quote_pattern = regex.compile(r'"([^"]*)"')
        Detector.__init__(self)

    def match(self, context):
        line_content = context.cur_line.content
        if not 'new' in line_content:
            return
        m = self.pattern.search(line_content)
        if m and not in_range(m.start(0), get_string_ranges(line_content)):
            args = m.group(1)[1:-1].split(',')
            for arg in args:
                m2 = self.quote_pattern.match(arg.strip())
                if m2:
                    fn = m2.group(1)
                    if is_abs_filename(fn) and not any(fn.startswith(key) for key in ("/etc/", "/dev/", "/proc")):
                        line_no = get_exact_lineno(m.start(0), context.cur_line)[1]
                        priority = MEDIUM_PRIORITY
                        if fn.startswith("/tmp"):
                            priority = LOW_PRIORITY
                        elif "/home" in fn:
                            priority = HIGH_PRIORITY
                        self.bug_accumulator.append(
                            BugInstance('DMI_HARDCODED_ABSOLUTE_FILENAME', priority, context.cur_patch.name, line_no,
                                        'Code contains a hard coded reference to an absolute pathname',
                                        sha=context.cur_patch.sha,
                                        line_content=context.cur_line.content)
                        )
