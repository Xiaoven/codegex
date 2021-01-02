class Detector:
    def __init__(self):
        self.bug_accumulator = []

    def match(self, linecontent: str, filename: str, lineno: int, **kwargs):
        """
        Match single line and generate bug instance using regex pattern
        :param get_exact_lineno:
        :param linecontent: line string to be search
        :param filename: file name
        :param lineno: line number in the file
        :return: None
        """
        pass

    def reset_bug_accumulator(self):
        self.bug_accumulator = list()