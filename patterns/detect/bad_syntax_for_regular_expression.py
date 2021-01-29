import regex

from patterns.models.detectors import Detector
from patterns.models.bug_instance import BugInstance
from patterns.models import priorities


class SingleDotPatternDetector(Detector):
    def __init__(self):
        self.pattern = regex.compile(r'\.\s*(replaceAll|replaceFirst|split|matches)\s*\(\s*"([.|])\s*"\s*,?([^)]*)')
        Detector.__init__(self)

    def match(self, linecontent: str, filename: str, lineno: int, **kwargs):
        if any(method in linecontent for method in ('replaceAll', 'replaceFirst', 'split', 'matches')) \
                and any(key in linecontent for key in ('"."', '"|"')):
            m = self.pattern.search(linecontent)
            if m:
                g = m.groups()
                method_name = g[0]
                arg_1 = g[1]
                arg_2 = g[2].strip()

                # Check number of parameter.
                # If method has more than 2 arguments, it might not be the one in String class.
                # arg_2 should look like `"replacement string, here"` or `var_name`.
                if ',' in arg_2 and not (arg_2.startswith('"') and arg_2.endswith('"')):
                    return

                priority = priorities.HIGH_PRIORITY
                if method_name == 'replaceAll' and arg_1 == '.':
                    priority = priorities.MEDIUM_PRIORITY
                    if arg_2.startswith('"') and arg_2.endswith('"'):
                        if arg_2 in ('"x"', '"X"', '"-"', '"*"', '" "', '"\\*"'):
                            return  # Ignore password mask
                        elif len(arg_2) == 3:
                            priority = priorities.LOW_PRIORITY

                self.bug_accumulator.append(BugInstance('RE_POSSIBLE_UNINTENDED_PATTERN', priority, filename, lineno,
                                                        '“.” or “|” used for regular expressions'))


class FileSeparatorAsRegexpDetector(Detector):
    def __init__(self):
        self.pattern = regex.compile(
            r'(\bPattern)?\.\s*(replaceAll|replaceFirst|split|matches|compile)\s*\(\s*File\.separator\s*,?([^)]*)')
        Detector.__init__(self)

    def match(self, linecontent: str, filename: str, lineno: int, **kwargs):
        if 'File.separator' in linecontent and any(
                method in linecontent for method in ('replaceAll', 'replaceFirst', 'split', 'matches', 'compile')):
            m = self.pattern.search(linecontent)
            if m:
                g = m.groups()
                class_name = g[0]
                method_name = g[1]
                arg_2 = g[2].strip()

                # Check number of parameter.
                if ',' in arg_2 and not (arg_2.startswith('"') and arg_2.endswith('"')):
                    return

                if method_name == 'compile' and (class_name != 'Pattern' or 'Pattern.LITERAL' in arg_2):
                    return

                priority = priorities.HIGH_PRIORITY
                if method_name == 'matches' and not arg_2:  # Observe from spotbugs' test cases
                    priority = priorities.LOW_PRIORITY

                self.bug_accumulator.append(
                    BugInstance('RE_CANT_USE_FILE_SEPARATOR_AS_REGULAR_EXPRESSION', priority, filename, lineno,
                                'File.separator used for regular expression'))
