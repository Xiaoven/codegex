from utils import log_message
from rparser import VirtualStatement
from gen_detectors import DETECTOR_DICT
from patterns.detect.inheritance_unsafe_get_resource import clear_cache


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

    def visit(self, patch_set):
        self.bug_accumulator = list()  # every patch set should own a new bug_accumulator
        for patch in patch_set:
            self._visit_patch(patch)

        # clean cache of GetResourceDetector for next patch_set which belongs to another project
        detector_name = 'GetResourceDetector'
        if detector_name in self._detectors:
            clear_cache()

    def _visit_patch(self, patch):
        """
        :param patch: code from a single file to visit
        :return: bug instances
        """
        pass

    def report(self):
        """
        This method is called after all patches to be visited.
        """
        for bug_ins in self.bug_accumulator:
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

                for detector in list(self._detectors.values()):
                    method = None
                    if isinstance(hunk.lines[i], VirtualStatement):
                        method = hunk.lines[i].get_exact_lineno
                    detector.match(line_content, patch.name, hunk.lines[i].lineno[1], method)

        # collect bug instances
        for detector in list(self._detectors.values()):
            if detector.bug_accumulator:
                self.bug_accumulator += detector.bug_accumulator
                detector.reset_bug_accumulator()
