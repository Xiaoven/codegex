import pytest

from codegex.models.context import Context
from codegex.models.engine import DefaultEngine
from codegex.utils.rparser import parse

params = [
    # https://github.com/javaee/glassfish/commit/211cbf351cab452c3d92836c7b1186f9ba8570e8
    (False, 'VO_VOLATILE_REFERENCE_TO_ARRAY', 'javaee/glassfish/SecureRMIServerSocketFactory.java',
     "private volatile String[] enabledCipherSuites = null;", 1, 1),
    # https://github.com/floscher/josm/commit/4aa395646d2d104b5395b490d5f493ad2a606644
    (False, 'VO_VOLATILE_REFERENCE_TO_ARRAY', 'floscher/josm/StayOpenCheckBoxMenuItem.java',
     "private static volatile MenuElement[] path;", 1, 1),
]


@pytest.mark.parametrize('is_patch,pattern_type,file_name,patch_str,expected_length,line_no', params)
def test(is_patch: bool, pattern_type: str, file_name: str, patch_str: str, expected_length: int, line_no: int):
    patch = parse(patch_str, is_patch)
    patch.name = file_name

    engine = DefaultEngine(Context(), included_filter=['VolatileArrayDetector'])
    engine.visit(patch)

    if expected_length > 0:
        assert len(engine.bug_accumulator) == expected_length
        assert engine.bug_accumulator[0].line_no == line_no
        assert engine.bug_accumulator[0].type == pattern_type
    else:
        assert len(engine.bug_accumulator) == 0
