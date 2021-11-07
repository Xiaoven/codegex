from collections import deque
from pathlib import PurePath
from loguru import logger


import jpype.imports

JARS_PATH = PurePath(__file__).parent.parent / 'dependencies' / 'jars'

jpype.startJVM(classpath=f'{JARS_PATH}/*')
import spoon.Launcher as Launcher
from spoon.reflect.cu.position import NoSourcePosition
from spoon.reflect.code import *
from spoon.reflect.declaration import *


def read_file_content(file_path: str):
    with open(file_path, 'r') as f:
        return f.read()


@logger.catch
def parse_ast(source: str, isPath=False):
    """
    Parse a given file into an AST
    :param source: class content or path of java file
    :return: root of the AST
    """
    content = source
    if isPath:
        with open(source, 'r') as f:
            content = f.read()
    return Launcher.parseClass(content)


def parse_ast_from_path(file_path: str):
    """
    Parse a given file into an AST
    :param file_path: path to specified file
    :return: root of the AST
    """
    content = read_file_content(file_path)
    return parse_ast(content)


@logger.catch
def build_map(ast_root):
    """
    Build the mapping between line number and AST nodes
    :param ast_root: CtElement, root node of an AST
    :return: a map with line number key and AST node value
    """
    lineNodeMap = dict()
    stack = deque()
    stack.append(ast_root)
    while stack:
        node = stack.pop()
        # Add node to lineNodeMap
        if not isinstance(node, CtBlock):
            try:
                position = node.getPosition()
                if isinstance(position, NoSourcePosition):
                    continue
                startLineNumber = position.getLine()
            except UnsupportedOperationException as e:
                logger.error("Position Type {}\n{}", type(position), e)
                continue

            if startLineNumber in lineNodeMap:
                lineNodeMap[startLineNumber].append(node)
            else:
                lineNodeMap[startLineNumber] = [node]

        # visit children
        if isinstance(node, (CtClass, CtBodyHolder, CtExecutable, CtStatementList)):
            if isinstance(node, CtBodyHolder):
                children = node.getBody().getDirectChildren()
            else:
                children = node.getDirectChildren()

            for child in children:
                if isinstance(child, (CtNamedElement, CtExecutable)) or \
                        (isinstance(child, CtStatement) and not isinstance(child, CtComment)):
                    stack.append(child)

    return lineNodeMap
