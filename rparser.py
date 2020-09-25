import re
from io import StringIO

class Hunk(object):
    """ Parsed hunk data container (hunk starts with @@ -R +R @@) """

    def __init__(self):
        '''
        :param startsrc: the line number of the start line in the source file
        :param linessrc: the number of lines of source files, including non-modified lines and deleted lines
        :param startsrc: the line number of the start line in the target file
        :param linessrc: the number of lines of source files, including non-modified lines and added lines
        :param lines: collections of Line objects
        :param dellines: indexes of deleted lines in @lines
        :param addlines: indexes of added lines in @lines
        '''
        self.startsrc = None  #: line count starts with 1
        self.linessrc = None
        self.starttgt = None
        self.linestgt = None
        self.lines = []
        self.dellines = []  # index of Line objects in self.text
        self.addlines = []

    def __iter__(self):
        for h in self.lines:
            yield h


class Line(object):
    def __init__(self, content, lineno=(-1, -1)):  # lineno的第一位是src里的lineno,第二位是tgt里的lineno
        self.content = content
        self.lineno = lineno

    def __str__(self):
        return self.content


class Patch(object):
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

    def parse(self, stream):
        re_hunk_start = re.compile(r'^@@ -(\d+),?(\d+)? \+(\d+),?(\d+)? @@.*?')
        f = StringIO(stream)
        hunk = None
        cnt_dict = {}
        for line in f:
            rst = re_hunk_start.match(line)
            if rst:
                if hunk:
                    self.hunks.append(hunk)

                g = rst.groups()
                hunk = Hunk()
                # fix case like '@@ -1 +1,21 @@'
                hunk.startsrc = int(g[0])
                hunk.linessrc = int(g[1]) if g[1] else 0
                hunk.starttgt = int(g[2])
                hunk.linestgt = int(g[3]) if g[3] else 0
                cnt_dict['linessrc'] = hunk.startsrc - 1
                cnt_dict['linestgt'] = hunk.starttgt - 1
            else:
                line_obj = None
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

        if hunk:
            self.hunks.append(hunk)