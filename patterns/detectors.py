import re


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
        pass

