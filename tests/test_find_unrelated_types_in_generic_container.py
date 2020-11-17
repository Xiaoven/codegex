from patterns.detect.find_unrelated_types_in_generic_container import FindUnrelatedTypesInGenericContainer
from rparser import Patch


class TestFindUnrelatedTypesInGenericContainer:
    # From other repositories: https://github.com/JMRI/JMRI/pull/6727/commits/407f386b0ec41b39cb4a0833d048d31f203f1b0f
    def test_DMI_USING_REMOVEALL_TO_CLEAR_COLLECTION_01(self):
        patch = Patch()
        patch.name = "OBlock.java"
        patch.parse('''@@ -963,6 +967,7 @@ public void dispose() {
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

    # From other repositories: https://github.com/erzhen1379/hbase2.1.4/blob/fc65d24aa0043529f3d44ad4b6e50835b0beb056/hbase-common/src/test/java/org/apache/hadoop/hbase/util/TestConcatenatedLists.java#L129
    def test_DMI_VACUOUS_SELF_COLLECTION_CALL_01(self):
        patch = Patch()
        patch.name = "TestConcatenatedLists.java"
        patch.parse('''@@ -963,6 +967,7 @@   private void verify(ConcatenatedLists<Long> c, int last) {
            assertEquals((last == -1), c.isEmpty());
            assertEquals(last + 1, c.size());
            assertTrue(c.containsAll(c));''')
        detector = FindUnrelatedTypesInGenericContainer()
        detector.visit([patch])
        assert len(detector.bug_accumulator) == 1
        assert detector.bug_accumulator[0].line_no == 969

    # DIY
    def test_DMI_VACUOUS_SELF_COLLECTION_CALL_02(self):
        patch = Patch()
        patch.name = "OBlock.java"
        patch.parse('''@@ -963,6 +967,7 @@   private void verify(ConcatenatedLists<Long> c, int last) {
            assertEquals((last == -1), c.isEmpty());
            assertEquals(last + 1, c.size());
            assertTrue(c.retainAll(c));''')
        detector = FindUnrelatedTypesInGenericContainer()
        detector.visit([patch])
        assert len(detector.bug_accumulator) == 1
        assert detector.bug_accumulator[0].line_no == 969

    # DIY
    def test_DMI_VACUOUS_SELF_COLLECTION_CALL_03(self):
        patch = Patch()
        patch.name = "OBlock.java"
        patch.parse('''@@ -963,6 +967,7 @@    private void verify(ConcatenatedLists<Long> c, int last) {
            assertEquals((last == -1), c.isEmpty());
            assertEquals(last + 1, c.size());
            assertTrue(c.getlist().retainAll(c.getlist()));''')
        detector = FindUnrelatedTypesInGenericContainer()
        detector.visit([patch])
        assert len(detector.bug_accumulator) == 1
        assert detector.bug_accumulator[0].line_no == 969

    # https://github.com/josephearl/findbugs/blob/fd7ec8b5cc0b1b143589674cdcdb901fa5dc0dda/findbugsTestCases/src/java/gcUnrelatedTypes/Ideas_2011_06_30.java#L13
    def test_DMI_COLLECTIONS_SHOULD_NOT_CONTAIN_THEMSELVES_01(self):
        patch = Patch()
        patch.name = "Ideas_2011_06_30.java"
        patch.parse('''@@ -963,6 +967,7 @@
                   @ExpectWarning("DMI_COLLECTIONS_SHOULD_NOT_CONTAIN_THEMSELVES")
                    public static void testTP(Collection<Integer> c) {
                        assertTrue(c.contains(c));
                    }''')
        detector = FindUnrelatedTypesInGenericContainer()
        detector.visit([patch])
        assert len(detector.bug_accumulator) == 1
        assert detector.bug_accumulator[0].line_no == 969

    # DIY
    def test_DMI_COLLECTIONS_SHOULD_NOT_CONTAIN_THEMSELVES_02(self):
        patch = Patch()
        patch.name = "Ideas_2011_06_30.java"
        patch.parse('''@@ -963,6 +967,7 @@
                        @ExpectWarning("DMI_COLLECTIONS_SHOULD_NOT_CONTAIN_THEMSELVES")
                        public static void testTP(Collection<Integer> c) {
                            return c.remove(c);
                        }
            ''')
        detector = FindUnrelatedTypesInGenericContainer()
        detector.visit([patch])
        assert len(detector.bug_accumulator) == 1
        assert detector.bug_accumulator[0].line_no == 969

    # DIY
    def test_DMI_COLLECTIONS_SHOULD_NOT_CONTAIN_THEMSELVES_03(self):
        patch = Patch()
        patch.name = "Ideas_2011_06_30.java"
        patch.parse('''@@ -963,6 +967,7 @@
                            @ExpectWarning("DMI_COLLECTIONS_SHOULD_NOT_CONTAIN_THEMSELVES")
                        public static void testTP(Collection<Integer> c) {
                            return c.getlist().remove(c.getlist());
                        }
            ''')
        detector = FindUnrelatedTypesInGenericContainer()
        detector.visit([patch])
        assert len(detector.bug_accumulator) == 1
        assert detector.bug_accumulator[0].line_no == 969
