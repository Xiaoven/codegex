import copy
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

    def __init__(self, line_obj: Line):
        super().__init__('', line_obj.lineno)
        self.sub_lines = []
        self.append_sub_line(line_obj)

    def append_sub_line(self, line_obj: Line):
        self.sub_lines.append(line_obj)
        content = line_obj.content
        if content.startswith(('+', '-')):
            content = content[1:]
        self.content += content



    def get_exact_lineno(self, key):
        '''
        Get exact line number
        :param key: match result to help find the exact line
        :return: line no
        '''
        for line in self.sub_lines:
            line_str = line.content
            if line_str.startswith(('-', '+')):
                line_str = line_str[1:]
            if key in line_str or line_str in key:
                return line.lineno
        return None


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
re_stmt_end = re.compile(r'[;{}](?:\s*//[^\n]*)?$')
re_annotation = re.compile(r'^@[\w\_$]+(?:\(.*\))?')


def _check_statement_end(line: str):
    """
    :param line: string without '+' or '-'
    :return: True or False
    """
    strip_line = line.strip()

    if (not strip_line) or re_stmt_end.search(strip_line) or re_annotation.match(strip_line) \
            or strip_line.endswith('*/') or strip_line.startswith('//'):
        return True
    return False


def _check_multiline_comment_start(line: str):
    return line.strip().startswith('/*')


def _check_multiline_comment_end(line: str):
    return line.strip().endswith('*/')


def _add_virtual_statement_to_hunk(vt_stmt: VirtualStatement, hunk: Hunk, prefix=''):
    if prefix == '+':
        hunk.addlines.append(len(hunk.lines))
    elif prefix == '-':
        hunk.dellines.append(len(hunk.lines))

    vt_stmt.content = prefix + vt_stmt.content
    hunk.lines.append(vt_stmt)


def _parse_hunk(stream, hunk=None):
    """
    Parse the content of a hunk
    :param stream: content to parse, exclude hunk header (i.e. '@@ -d,d +d,d @@')
    :param hunk: a hunk object with info
    :return: the hunk object
    """
    cnt_dict = {'linessrc': hunk.startsrc - 1, 'linestgt': hunk.starttgt - 1}

    # init statement. Priority: del_statement == add_statement > common_statement
    del_statement = None
    add_statement = None
    common_statement = None
    # del_multi_comment = False
    # add_multi_comment = False
    # if a common_statement meets a del_statement, the first 'False' will be 'True',
    # similar relationship to the second 'False' and add_statement
    incomplete_common_statement = [False, False]

    for line in StringIO(stream):
        # -------------------------- Del line -----------------------------
        if line.startswith("-"):
            cnt_dict['linessrc'] += 1
            line_obj = Line(line, (cnt_dict['linessrc'], -1))

            if common_statement:
                incomplete_common_statement[0] = True

            # if _check_multiline_comment_start(line[1:]):
            #     del_multi_comment = True
            #     if del_statement:
            #         # store the last del_statement
            #         hunk.dellines.append(len(hunk.lines))
            #         del_statement.content = '-' + del_statement.content
            #         hunk.lines.append(del_statement)
            #     # new a del_statement for the multiline comment
            #     del_statement = VirtualStatement(line_obj)
            #     # then goto reset common_statement
            # elif del_multi_comment:
            #     if _check_multiline_comment_end(line[1:]):
            #         if not del_statement and common_statement:
            #             del_statement = copy.deepcopy(common_statement)
            #         del_statement.append_sub_line(line_obj)
            #         del_statement.content = '-' + del_statement.content
            #         hunk.lines.append(del_statement)
            #         del_statement = None
            #     else:
            #         if not del_statement and common_statement:
            #             del_statement = copy.deepcopy(common_statement)
            #         del_statement.append_sub_line(line_obj)  # then goto reset common_statement
            # elif _check_statement_end(line[1:]):  # whether line is a complete statement or not

            if _check_statement_end(line[1:]):  # whether line is a complete statement or not
                if not (common_statement or del_statement):
                    hunk.dellines.append(len(hunk.lines))
                    hunk.lines.append(line_obj)
                    continue
                # line_obj belongs to a del_statement
                if not del_statement and common_statement:
                    del_statement = copy.deepcopy(common_statement)
                del_statement.append_sub_line(line_obj)
                # del_statement.content = '-' + del_statement.content
                # hunk.lines.append(del_statement)
                _add_virtual_statement_to_hunk(del_statement, hunk, '-')
                del_statement = None
            else:
                # if line_obj is a incomplete statement, it must belong to del_statement
                if not del_statement:
                    if common_statement:
                        del_statement = copy.deepcopy(common_statement)
                        del_statement.append_sub_line(line_obj)
                    else:
                        del_statement = VirtualStatement(line_obj)
        # -------------------------- Add line -----------------------------
        elif line.startswith("+"):
            cnt_dict['linestgt'] += 1
            line_obj = Line(line, (-1, cnt_dict['linestgt']))

            if common_statement:
                incomplete_common_statement[1] = True

            # if _check_multiline_comment_start(line[1:]):
            #     add_multi_comment = True
            #     if add_statement:
            #         # store the last add_statement
            #         hunk.addlines.append(len(hunk.lines))
            #         add_statement.content = '+' + add_statement.content
            #         hunk.lines.append(add_statement)
            #     # new a add_statement for the multiline comment
            #     add_statement = VirtualStatement(line_obj)
            #     # then goto reset common_statement
            # elif add_multi_comment:
            #     if _check_multiline_comment_end(line[1:]):
            #         if not add_statement and common_statement:
            #             add_statement = copy.deepcopy(common_statement)
            #         add_statement.append_sub_line(line_obj)
            #         add_statement.content = '+' + add_statement.content
            #         hunk.lines.append(add_statement)
            #         add_statement = None
            #     else:
            #         if not add_statement and common_statement:
            #             add_statement = copy.deepcopy(common_statement)
            #         add_statement.append_sub_line(line_obj)  # then goto reset common_statement
            # elif _check_statement_end(line[1:]):

            if _check_statement_end(line[1:]):
                if not (common_statement or add_statement):
                    hunk.addlines.append(len(hunk.lines))
                    hunk.lines.append(line_obj)
                    continue

                # line_obj belongs to a add_statement
                if common_statement and not add_statement:
                    add_statement = copy.deepcopy(common_statement)
                add_statement.append_sub_line(line_obj)
                # add_statement.content = '+' + add_statement.content
                # hunk.lines.append(add_statement)
                #
                _add_virtual_statement_to_hunk(add_statement, hunk, '+')
                add_statement = None
            else:
                # if line_obj is a incomplete statement, it must belong to add_statement
                if not add_statement:
                    if common_statement:
                        add_statement = copy.deepcopy(common_statement)
                        add_statement.append_sub_line(line_obj)
                    else:
                        add_statement = VirtualStatement(line_obj)
        # -------------------------- common line -----------------------------
        else:
            cnt_dict['linessrc'] += 1
            cnt_dict['linestgt'] += 1
            line_obj = Line(line, (cnt_dict['linessrc'], cnt_dict['linestgt']))

            # if _check_multiline_comment_start(line[1:]):
            #     add_multi_comment = True
            #     del_multi_comment = True
            #
            #     if common_statement:
            #         common_statement.append_sub_line(line_obj)
            #         hunk.lines.append(common_statement)
            #     common_statement = VirtualStatement(line_obj)
            #
            #     if del_statement:
            #         del_statement.append_sub_line(line_obj)
            #         del_statement.content = '-' + del_statement.content
            #         hunk.lines.append(del_statement)
            #         del_statement = None
            #     if add_statement:
            #         add_statement.append_sub_line(line_obj)
            #         add_statement.content = '+' + add_statement.content
            #         hunk.lines.append(add_statement)
            #         add_statement = None
            #
            # elif add_multi_comment or del_multi_comment:
            #     if not _check_multiline_comment_end(line[1:]):
            #         if common_statement:
            #             common_statement.append_sub_line(line_obj)

            if _check_statement_end(line):

                if not (common_statement or del_statement or add_statement):
                    hunk.lines.append(line_obj)
                    continue

                # if both add_statement and del_statement are not None, common_statement must be none
                if common_statement:
                    common_statement.append_sub_line(line_obj)
                    # hunk.lines.append(common_statement)
                    #
                    _add_virtual_statement_to_hunk(common_statement, hunk)
                    common_statement = None
                if del_statement:
                    del_statement.append_sub_line(line_obj)
                    # del_statement.content = '-' + del_statement.content
                    # hunk.lines.append(del_statement)
                    #
                    _add_virtual_statement_to_hunk(del_statement, hunk, '-')
                    del_statement = None
                if add_statement:
                    add_statement.append_sub_line(line_obj)
                    # add_statement.content = '+' + add_statement.content
                    # hunk.lines.append(add_statement)
                    #
                    _add_virtual_statement_to_hunk(add_statement, hunk, '+')
                    add_statement = None
            else:
                if not (common_statement or add_statement or del_statement):
                    common_statement = VirtualStatement(line_obj)
                    continue

                if common_statement:
                    common_statement.append_sub_line(line_obj)
                if del_statement:
                    del_statement.append_sub_line(line_obj)
                if add_statement:
                    add_statement.append_sub_line(line_obj)
        # -------------------------- Reset Common_Statement -----------------------------
        if incomplete_common_statement[0] and incomplete_common_statement[1]:
            common_statement = None
            incomplete_common_statement[0], incomplete_common_statement[1] = False, False

    if common_statement:
        hunk.lines.append(common_statement)

    if del_statement:
        _add_virtual_statement_to_hunk(del_statement, hunk, '-')

    if add_statement:
        _add_virtual_statement_to_hunk(add_statement, hunk, '+')

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
            _parse_hunk(hunk_content, patch.hunks[i - 1])
            last_end = hunk_bounds[i][1]
        _parse_hunk(stream[last_end:], patch.hunks[-1])

    return patch
