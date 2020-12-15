import re

from patterns.detectors import Detector
from patterns.bug_instance import BugInstance
import patterns.priorities as Priorities


class DefSerialVersionID(Detector):
    def __init__(self):
        self.pattern = re.compile(r'((?:static|final|\s)*)\b(long|int)\s+serialVersionUID\b')
        Detector.__init__(self)

    def match(self, linecontent: str, filename: str, lineno: int, get_exact_lineno=None):
        if 'serialVersionUID' not in linecontent:
            return

        m = self.pattern.search(linecontent)
        if m:
            g = m.groups()
            prefix = None
            g1 = g[0].strip()
            if g1:
                prefix = g1.split()

            pattern_name = None
            message = None
            priority = Priorities.LOW_PRIORITY

            if prefix:
                if 'static' not in prefix:
                    pattern_name = 'SE_NONSTATIC_SERIALVERSIONID'
                    message = "serialVersionUID isn't static."
                    priority = Priorities.NORMAL_PRIORITY
                elif 'final' not in prefix:
                    pattern_name = 'SE_NONFINAL_SERIALVERSIONID'
                    message = "serialVersionUID isn't final."
                    priority = Priorities.NORMAL_PRIORITY

            if not pattern_name and 'int' == g[1]:
                pattern_name = 'SE_NONLONG_SERIALVERSIONID'
                message = "serialVersionUID isn't long."

            if pattern_name:
                self.bug_accumulator.append(
                    BugInstance(pattern_name, priority, filename, lineno, message))


class DefReadResolveMethod(Detector):
    def __init__(self):
        self.pattern = re.compile(
            r'((?:static|final|\s)*)\b([^\s]+)\s+readResolve\s*\(\s*\)\s+throws\s+ObjectStreamException')
        Detector.__init__(self)

    def match(self, linecontent: str, filename: str, lineno: int, get_exact_lineno=None):
        if any(const not in linecontent for const in ['readResolve', 'throws', 'ObjectStreamException']):
            return

        m = self.pattern.search(linecontent)
        if m:
            g = m.groups()

            pattern_name = None
            message = None

            if g[1] != 'Object':
                pattern_name = 'SE_READ_RESOLVE_MUST_RETURN_OBJECT'
                message = 'The readResolve method must be declared with a return type of Object.'
            elif g[0] and 'static' in g[0].split():
                pattern_name = 'SE_READ_RESOLVE_IS_STATIC'
                message = 'The readResolve method must not be declared as a static method.'

            if pattern_name:
                self.bug_accumulator.append(
                    BugInstance(pattern_name, Priorities.NORMAL_PRIORITY, filename, lineno, message))




