from patterns.utils import logger, is_comment
from rparser import VirtualStatement
from timer import Timer


class BaseEngine:
    '''
    The interface which all bug pattern detectors must implement.
    '''

    def visit(self, patchSet):
        self.bug_accumulator = list()  # every patch set should own a new bug_accumulator
        for patch in patchSet:
            self._visit_patch(patch)

    def _visit_patch(self, patch):
        '''
        :param patch: code from a single file to visit
        :return: bug instances
        '''
        pass

    def report(self):
        '''
        This method is called after all patches to be visited.
        '''
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
                if i in hunk.addlines:
                    line_content = line_content[1:]  # remove "+"

                line_content = line_content.strip()
                if not line_content or line_content.startswith('//'):
                    continue

                # skip multiline comments
                if line_content.startswith('/*'):
                    if not line_content.endswith('*/'):
                        in_multiline_comments = True
                    continue

                if in_multiline_comments:
                    if line_content.endswith('*/'):
                        in_multiline_comments = False
                    continue

                for detector in self.detectors:
                    t = Timer(name=detector.__class__.__name__, logger=None)
                    t.start()
                    method = None
                    if isinstance(hunk.lines[i], VirtualStatement):
                        method = hunk.lines[i].get_exact_lineno
                    detector.match(line_content, patch.name, hunk.lines[i].lineno[1], method)
                    t.stop()

        # collect bug instances
        for detector in self.detectors:
            if detector.bug_accumulator:
                self.bug_accumulator += detector.bug_accumulator
                detector.reset()


class Detector:
    def __init__(self):
        self.bug_accumulator = []

    def match(self, linecontent: str, filename: str, lineno: int, get_exact_lineno=None):
        '''
        Match single line and generate bug instance using regex pattern
        :param get_exact_lineno:
        :param linecontent: line string to be search
        :param filename: file name
        :param lineno: line number in the file
        :return: None
        '''
        pass

    def reset(self):
        self.bug_accumulator = list()
