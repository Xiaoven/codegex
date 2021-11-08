class Hunk:
    """ Parsed hunk data container (hunk starts with @@ -R +R @@) """

    def __init__(self, startsrc=1, linessrc=0, starttgt=1, linestgt=0):
        """
        :param startsrc: the line number of the start line in the source file
        :param linessrc: the number of lines of source files, including non-modified lines and deleted lines
        :param startsrc: the line number of the start line in the target file
        :param linessrc: the number of lines of source files, including non-modified lines and added lines
        :param lines: collections of Line objects
        :param dellines: indexes of deleted lines in @lines
        :param addlines: indexes of added lines in @lines
        """
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
    def __init__(self, content, lineno=(-1, -1), is_patch=True):
        """
        :param content: line content
        :param lineno: line numbers in src and tgt separately
        :param is_patch: whether a modified line prefixed with '+' or '-'
        """
        self.lineno = lineno
        if is_patch and len(content) > 1:
            # In patch, the first character is reserved to indicate if the line is deleted or added
            self.prefix = content[0].strip()
            self.content = content[1:]
        else:
            self.prefix = ''
            self.content = content

    def __str__(self):
        if self.prefix:
            return self.prefix + self.content
        else:
            return self.content


class VirtualStatement(Line):
    """
    A virtual statement contains multiple lines ending with '\n'.
    It ends with ';', '{' or '}'. Its prefix should be set manually.
    """

    def __init__(self, line_obj: Line):
        super().__init__('', line_obj.lineno)
        self.sub_lines = []
        self.append_sub_line(line_obj)

    def append_sub_line(self, line_obj: Line):
        self.sub_lines.append(line_obj)
        self.content += line_obj.content

    def merge_vt_stmt(self, vt_stmt):
        self.sub_lines.extend(vt_stmt.sub_lines)
        self.content += vt_stmt.content

    def get_exact_lineno_by_keyword(self, key: str):
        """
        Get exact line number by keyword
        :param key: keyword string
        :return: lineno of Line object, or None if fail
        """
        for line in self.sub_lines:
            if key in line.content or line.content in key:
                return line.lineno
        return None

    def get_exact_lineno_by_offset(self, offset: int, if_strip=False):
        """
        Get exact line number by offset in line content
        :param offset: offset in line content string
        :param if_strip: if true, left strip the first sub-line and right strip the last sub-line
        :return: lineno of Line object, or None for invalid offset
        """
        size = len(self.sub_lines)
        i = 0
        while i < size:
            if i == 0 and if_strip:
                offset -= len(self.sub_lines[i].content.lstrip())
            elif i == size - 1 and if_strip:
                offset -= len(self.sub_lines[i].content.rstrip())
            else:
                offset -= len(self.sub_lines[i].content)

            if offset <= 0:
                return self.sub_lines[i].lineno

            i += 1
        return None


class Patch:
    """ Patch for a single file.
        If used as an iterable, returns hunks.
    """

    def __init__(self):
        self.name = ''
        self.hunks = []
        self.type = None
        self.sha = ''

    def __iter__(self):
        for h in self.hunks:
            yield h
