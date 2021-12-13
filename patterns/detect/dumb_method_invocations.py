import regex

from patterns.models.priorities import *
from patterns.models.bug_instance import BugInstance
from patterns.models.detectors import Detector, get_exact_lineno
import os

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
                            'This code invokes substring(0) on a String, which returns the original value.', sha=context.cur_patch.sha,
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
        self.pattern = regex.compile(r'\bnew\s+(?:File|RandomAccessFile|Paths|FileReader|FileWriter|FileInputStream|FileOutputStream|Formatter|JarFile|ZipFile|PrintStream|PrintWriter)\s*(?P<aux1>\((?:[^()]++|(?&aux1))*\))')
        Detector.__init__(self)

    def match(self, context):
        line_content = context.cur_line.content
        if not 'new' in line_content:
            return
        m = self.pattern.search(line_content)
        if m:
            args = m.groups()[0]
            print("@@@", args)
            p = regex.compile(r'"([^"]*)"')
            for fn in p.findall(args):
                if is_abs_filename(fn) and not fn.startswith("/etc/") and not fn.startswith("/dev/") and not fn.startswith("/proc"):
                    line_no = get_exact_lineno(m.start(0), context.cur_line)[1]
                    self.bug_accumulator.append(
                        BugInstance('DMI_HARDCODED_ABSOLUTE_FILENAME', MEDIUM_PRIORITY, context.cur_patch.name, line_no,
                                    'This code constructs a File object using a hard coded to an absolute pathname (e.g., '
                                    'new File("/home/dannyc/workspace/j2ee/src/share/com/sun/enterprise/deployment");',
                                    sha=context.cur_patch.sha,
                                    line_content=context.cur_line.content)
                    )
