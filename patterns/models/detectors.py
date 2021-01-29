from patterns.models.context import Context


class Detector:
    def __init__(self):
        self.bug_accumulator = []

    def match(self, context: Context):
        """
        Match single line and generate bug instance using regex pattern
        :param context: context object
        :return: None
        """
        pass

    def reset_bug_accumulator(self):
        self.bug_accumulator = list()