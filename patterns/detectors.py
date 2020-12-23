from patterns.utils import logger
from rparser import VirtualStatement


class BaseEngine:
    """
    The interface which all bug pattern detectors must implement.
    """

    def visit(self, patchSet):
        self.bug_accumulator = list()  # every patch set should own a new bug_accumulator
        for patch in patchSet:
            self._visit_patch(patch)

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
            logger.warning(str(bug_ins))


class DefaultEngine(BaseEngine):
    """
    ParentDetector and SubDetector are for multiple single-line patterns in the same file
    """

    def __init__(self, detectors: list):
        """
        Init the parent detector
        :param detectors: SubDetectors
        """
        self.detectors = detectors

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

                for detector in self.detectors:
                    method = None
                    if isinstance(hunk.lines[i], VirtualStatement):
                        method = hunk.lines[i].get_exact_lineno
                    detector.match(line_content, patch.name, hunk.lines[i].lineno[1], method)

        # collect bug instances
        for detector in self.detectors:
            if detector.bug_accumulator:
                self.bug_accumulator += detector.bug_accumulator
                detector.reset()


class Detector:
    def __init__(self):
        self.bug_accumulator = []

    def match(self, linecontent: str, filename: str, lineno: int, get_exact_lineno=None):
        """
        Match single line and generate bug instance using regex pattern
        :param get_exact_lineno:
        :param linecontent: line string to be search
        :param filename: file name
        :param lineno: line number in the file
        :return: None
        """
        pass

    def reset(self):
        self.bug_accumulator = list()
