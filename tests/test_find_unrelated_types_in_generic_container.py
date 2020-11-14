from patterns.detect.find_unrelated_types_in_generic_container import FindUnrelatedTypesInGenericContainer
from rparser import Patch


class TestFindUnrelatedTypesInGenericContainer:
    # From other repositories: https://github.com/JMRI/JMRI/pull/6727/commits/407f386b0ec41b39cb4a0833d048d31f203f1b0f
    def test_DMI_USING_REMOVEALL_TO_CLEAR_COLLECTION_01(self):
        patch = Patch()
        patch.name = "OBlock.java"
        patch.parse('''@@ -963,6 +967,7 @@ public void dispose() {                 sda
            // remove portal and stub paths through portal in opposing block
            opBlock.removePortal(portal);
        }
        _portals.removeAll(_portals);
        List<Path> pathList = getPaths();
        for (int i = 0; i < pathList.size(); i++) {
            removePath(pathList.get(i));''')
        detector = FindUnrelatedTypesInGenericContainer()
        detector.visit([patch])
        assert len(detector.bug_accumulator) == 1
        assert detector.bug_accumulator[0].line_no == 970