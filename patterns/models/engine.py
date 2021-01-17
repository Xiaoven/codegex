from utils import log_message
from rparser import VirtualStatement
from gen_detectors import DETECTOR_DICT
from patterns.detect.inheritance_unsafe_get_resource import clear_cache
from .priorities import *


class BaseEngine:
    """
    The interface which all bug pattern detectors must implement.
    """

    def __init__(self, included_filter=None, excluded_filter=None):
        """
        Init detectors according to included_filter or excluded_filter
        :param included_filter: a list or tuple of detector class names to include
        :param excluded_filter: a list or tuple of detector class names to exclude
        """
        self.bug_accumulator = list()  # every patch set should own a new bug_accumulator
        self._detectors = dict()

        if included_filter:
            for name in included_filter:
                detector_class = DETECTOR_DICT.get(name, None)
                if detector_class:
                    self._detectors[name] = detector_class()
        elif excluded_filter:
            for name, detector_class in DETECTOR_DICT.items():
                if name not in excluded_filter:
                    self._detectors[name] = detector_class()
        else:
            for name, detector_class in DETECTOR_DICT.items():
                self._detectors[name] = detector_class()

    def _init_extends_dict(self, patch_set):
        # is this name visible in the current scope:
        if 'GENERIC_REGEX' not in dir():
            from patterns.detect.naming import GENERIC_REGEX, CLASS_EXTENDS_REGEX, INTERFACE_EXTENDS_REGEX

        visible_name_in_cur_scope = dir()
        assert all(regexp in visible_name_in_cur_scope for regexp in
                   ('GENERIC_REGEX', 'CLASS_EXTENDS_REGEX', 'INTERFACE_EXTENDS_REGEX'))

        self.extends_dict = dict()
        for patch in patch_set:
            extended_names_in_patch = set()
            for hunk in patch:
                for line in hunk:
                    if line.prefix == '-':
                        continue

                    if 'extends' in line.content:
                        if 'class' in line.content:
                            m = CLASS_EXTENDS_REGEX.search(line.content.strip())
                        elif 'interface' in line.content:
                            m = INTERFACE_EXTENDS_REGEX.search(line.content.strip())
                        else:
                            continue

                        if m:
                            g = m.groups()
                            extended_str = GENERIC_REGEX.sub('', g[-1])  # remove <...>
                            extended_names_in_line = [name.rsplit('.', 1)[-1].strip() for name in
                                                      extended_str.split(',')]
                            extended_names_in_patch.update(extended_names_in_line)

            self.extends_dict[patch.name] = extended_names_in_patch

    def _local_search(self, simple_name):
        assert hasattr(self, 'extends_dict')
        for patch_name, extended_name_list in self.extends_dict.items():
            if simple_name in extended_name_list:
                return simple_name
        return None

    def visit(self, *patch_set):
        detector_name = 'GetResourceDetector'
        if detector_name in self._detectors:
            # clean cache of GetResourceDetector for next patch_set which belongs to another project for online search
            clear_cache()
            self._init_extends_dict(patch_set)

        self.bug_accumulator = list()  # reset

        for patch in patch_set:
            self._visit_patch(patch)

    def _visit_patch(self, patch):
        """
        :param patch: code from a single file to visit
        :return: bug instances
        """
        pass

    def filter_bugs(self, level=None):
        if not level:
            return self.bug_accumulator

        if level == 'low':
            bound = LOW_PRIORITY
        elif level == 'medium':
            bound = MEDIUM_PRIORITY
        elif level == 'high':
            bound = HIGH_PRIORITY
        elif level == 'exp':
            bound = EXP_PRIORITY
        elif level == 'ignore':
            bound = IGNORE_PRIORITY
        else:
            raise ValueError('Invalid level value. Hint: ignore, exp, low, medium, high')

        return tuple(bug for bug in self.bug_accumulator if bug.priority <= bound)

    def report(self, level='low'):
        """
        This method is called after all patches to be visited.
        """
        for bug_ins in self.filter_bugs(level):
            log_message(str(bug_ins), 'info')


class DefaultEngine(BaseEngine):
    """
    ParentDetector and SubDetector are for multiple single-line patterns in the same file
    """

    def _visit_patch(self, patch):
        """
        Scan the patch using sub-detectors and generate bug instances
        :param patch:
        :return: None
        """
        in_multiline_comments = False
        # detect patch
        for hunk in patch:
            for i in range(len(hunk.lines)):
                # detect all lines in the patch rather than the addition
                if i in hunk.dellines:
                    continue

                line_content = hunk.lines[i].content

                for name, detector in self._detectors.items():
                    method_dict = dict()
                    if isinstance(hunk.lines[i], VirtualStatement):
                        method_dict['get_exact_lineno'] = hunk.lines[i].get_exact_lineno

                    if name == 'GetResourceDetector':
                        method_dict['local_search'] = self._local_search

                    detector.match(line_content, patch.name, hunk.lines[i].lineno[1], **method_dict)

        # collect bug instances
        for detector in list(self._detectors.values()):
            if detector.bug_accumulator:
                self.bug_accumulator += detector.bug_accumulator
                detector.reset_bug_accumulator()
