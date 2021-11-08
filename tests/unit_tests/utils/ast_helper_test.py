from utils.ast_helper import *

TEST_SOURCE = PurePath(__file__).parent.parent / 'resources/MapMaterial.java'


def test_build_map():
    root = parse_ast(TEST_SOURCE, isPath=True)
    mappings = build_map(root)

    assert len(mappings) == 20

    # [CtAnonymousExecutable] static code block
    assert len(mappings[4]) == 1 and isinstance(mappings[4][0], CtAnonymousExecutable)
    assert len(mappings[5]) == 1 and isinstance(mappings[5][0], CtLocalVariable)

    # 2 elements in one line
    assert len(mappings[34]) == 2 and isinstance(mappings[34][0], CtMethod) and isinstance(mappings[34][1], CtReturn)
    assert len(mappings[21]) == 2 and isinstance(mappings[21][0], CtForEach) and isinstance(mappings[21][1], CtInvocation)
