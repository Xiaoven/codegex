import re
from io import StringIO


class Hunk:
    """ Parsed hunk data container (hunk starts with @@ -R +R @@) """

    def __init__(self, startsrc=1, linessrc=0, starttgt=1, linestgt=0):
        '''
        :param startsrc: the line number of the start line in the source file
        :param linessrc: the number of lines of source files, including non-modified lines and deleted lines
        :param startsrc: the line number of the start line in the target file
        :param linessrc: the number of lines of source files, including non-modified lines and added lines
        :param lines: collections of Line objects
        :param dellines: indexes of deleted lines in @lines
        :param addlines: indexes of added lines in @lines
        '''
        self.startsrc = startsrc  #: line count starts with 1
        self.linessrc = linessrc
        self.starttgt = starttgt
        self.linestgt = linestgt
        self.lines = []
        self.dellines = []  # index of Line objects in self.text
        self.addlines = []

    def __iter__(self):
        for h in self.lines:
            yield h


class Line:
    def __init__(self, content, lineno=(-1, -1)):  # lineno的第一位是src里的lineno,第二位是tgt里的lineno
        self.content = content
        self.lineno = lineno

    def __str__(self):
        return self.content


class VirtualStatement(Line):
    """
    A virtual statement contains multiple lines ending with '\n'.
    It ends with ';', '{' or '}'
    """

    def __init__(self, content: str, lineno=(-1, -1)):
        super.__init__(self)
        self.sub_lines = []


class Patch:
    """ Patch for a single file.
        If used as an iterable, returns hunks.
    """

    def __init__(self):
        self.name = None
        self.hunks = []
        self.type = None

    def __iter__(self):
        for h in self.hunks:
            yield h


# --------------------------------------------------------------------------------------
def _parse_hunk(stream, hunk=None):
    """
    Parse the content of a hunk
    :param stream: content to parse, exclude hunk header (i.e. '@@ -d,d +d,d @@')
    :param hunk: a hunk object with info
    :return: the hunk object
    """
    cnt_dict = {'linessrc': hunk.startsrc - 1, 'linestgt': hunk.starttgt - 1}

    for line in StringIO(stream):
        if line.startswith("-"):
            cnt_dict['linessrc'] += 1
            line_obj = Line(line, (cnt_dict['linessrc'], -1))
            hunk.dellines.append(len(hunk.lines))
        elif line.startswith("+"):
            cnt_dict['linestgt'] += 1
            line_obj = Line(line, (-1, cnt_dict['linestgt']))
            hunk.addlines.append(len(hunk.lines))
        else:
            cnt_dict['linessrc'] += 1
            cnt_dict['linestgt'] += 1
            line_obj = Line(line, (cnt_dict['linessrc'], cnt_dict['linestgt']))

        hunk.lines.append(line_obj)
    return hunk


re_hunk_start = re.compile(r'^@@ -(\d+),?(\d+)? \+(\d+),?(\d+)? @@[^\n]*\n')


def parse(stream, is_patch=True):
    """
    parse modifications of a file
    :param stream: content of a patch or a hunk
    :param is_patch: stream contains lines like '@@ -d,d +d,d @@' or not
    :return: a patch object
    """

    patch = Patch()

    if not is_patch:
        patch.hunks.append(_parse_hunk(stream, Hunk()))
    else:
        hunk_bounds = []

        matches = re_hunk_start.finditer(stream)
        for match in matches:
            g = match.groups()
            startsrc = int(g[0])
            linessrc = int(g[1]) if g[1] else 0  # fix case like '@@ -1 +1,21 @@'
            starttgt = int(g[2])
            linestgt = int(g[3]) if g[3] else 0

            patch.hunks.append(Hunk(startsrc, linessrc, starttgt, linestgt))
            hunk_bounds.append((match.start(), match.end()))

        last_end = hunk_bounds[0][1]
        for i in range(1, len(hunk_bounds)):
            hunk_content = stream[last_end:hunk_bounds[i][0]]
            _parse_hunk(hunk_content, patch.hunks[i-1])
            last_end = hunk_bounds[i][1]
        _parse_hunk(stream[last_end:], patch.hunks[-1])

    return patch
