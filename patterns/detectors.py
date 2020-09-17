from patterns.utils import logger
class Detector:
    '''
    The interface which all bug pattern detectors must implement.
    '''

    def visit(self, patchSet):
        self.bug_accumulator = []
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

class SubDetector:
    '''
    For single line pattern
    '''
    def __init__(self):
        self.bug_accumulator = []

    def match(self, linecontent: str, filename: str, lineno: int):
        '''
        Match single line and generate bug instance using regex pattern
        :param linecontent: line string to be search
        :param filename: file name
        :param lineno: line number in the file
        :return: None
        '''
        pass