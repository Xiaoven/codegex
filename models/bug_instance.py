from enum import unique, Enum


@unique
class Confidence(Enum):
    # priority for bug instances that should be ignored
    IGNORE = 5
    # Experimental priority for bug instances.
    EXPERIMENTAL = 4
    # Low priority for bug instances.
    LOW = 3
    # Normal priority for bug instances
    MEDIUM = 2
    # High priority for bug instances.
    HIGH = 1


class BugInstance:
    def __init__(self, pattern_type: str, confidence: Confidence, file_name: str, line_no: int, description='', sha='',
                 line_content=''):
        self.type = pattern_type
        self.file_name = file_name
        self.commit_sha = sha
        self.line_no = line_no
        self.confidence = confidence
        self.description = description
        self.line_content = line_content

    def __str__(self):
        return '%s:%s:%s:%s' % (self.file_name, self.line_no, self.confidence.name, self.type)
