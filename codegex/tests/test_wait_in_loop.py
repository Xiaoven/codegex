import pytest

from codegex.models.context import Context
from codegex.models.engine import DefaultEngine
from codegex.utils.rparser import parse

params = [
    # https://github.com/javaee/glassfish/commit/566f8ba3b206a3ca97a24d3d62acfa894fb21553
    (True, 'NO_NOTIFY_NOT_NOTIFYALL', 'javaee/glassfish/MessageBeanContainer.java.java',
     '''@@ -958,7 +958,7 @@ public void run() {
            } finally {
                synchronized (this) {
                    this.done = true;
                    this.notify();
                }
                try {
                    mdbPool.close();''', 1, 961),
]


@pytest.mark.parametrize('is_patch,pattern_type,file_name,patch_str,expected_length,line_no', params)
def test(is_patch: bool, pattern_type: str, file_name: str, patch_str: str, expected_length: int, line_no: int):
    patch = parse(patch_str, is_patch)
    patch.name = file_name

    engine = DefaultEngine(Context(), included_filter=['NotifyDetector'])
    engine.visit(patch)

    if expected_length > 0:
        assert len(engine.bug_accumulator) == expected_length
        assert engine.bug_accumulator[0].line_no == line_no
        assert engine.bug_accumulator[0].type == pattern_type
    else:
        assert len(engine.bug_accumulator) == 0
