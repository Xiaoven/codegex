import pytest

from patterns.detect.incompat_mask import *
from patterns.detectors import DefaultEngine
from rparser import parse
from patterns.priorities import *

params = [
    # From other repository: https://github.com/albfan/jmeld/commit/bab5df4d96b511dd1e4be36fce3a2eab52c24c4e
    (True, 'BIT_SIGNED_CHECK', "Fake.java",
     '''@@ -51,7 +51,7 @@ public void hierarchyChanged(HierarchyEvent e)
         {
           JRootPane rootPane;
 
          if ((e.getChangeFlags() & 1) > 0)
           {
             rootPane = getRootPane();
             if (rootPane == null)}''', 1, 54),
    # From other repository: https://github.com/bndtools/bnd/commit/68c73f78ef7de5234714b350a7d0b8760f9eaf1a
    (True, 'BIT_SIGNED_CHECK', "Fake.java",
     '''@@ -222,7 +222,7 @@ public void resourceChanged(IResourceChangeEvent event) {
         if (delta == null)
             return;
 
+        if ((delta.getKind() & 4) > 0 && (delta.getFlags() & MARKERS) > 0) {
             getEditorSite().getShell().getDisplay().asyncExec(new Runnable() {
                 public void run() {
                     loadProblems();''', 1, 225),
    # DIY from https://github.com/SpigotMC/BungeeCord/blob/master/protocol/src/main/java/net/md_5/bungee/protocol/Varint21LengthFieldPrepender.java
    (False, 'BIT_AND_ZZ', 'Varint21LengthFieldPrepender.java',
     '''private static int varintSize(int paramInt){
            if ( ( paramInt & 0xFFFFFF80 ) == 0 ) { return 1;}
            if ( ( paramInt & 0xFFFFC000 ) == 0 ) { return 2;}
            if ( ( paramInt & 0x00000000 ) == 0 ) { return 3;}
            if ( ( paramInt & 0xF0000000 ) == 0 ) { return 4;}
            return 5;
        }''', 1, 4),
]


@pytest.mark.parametrize('is_patch,pattern_type,file_name,patch_str,expected_length,line_no', params)
def test(is_patch: bool, pattern_type: str, file_name: str, patch_str: str, expected_length: int,
         line_no: int):
    patch = parse(patch_str, is_patch)
    patch.name = file_name
    engine = DefaultEngine([IncompatMaskDetector()])
    engine.visit([patch])
    if expected_length > 0:
        assert len(engine.bug_accumulator) == expected_length
        assert engine.bug_accumulator[0].line_no == line_no
        assert engine.bug_accumulator[0].type == pattern_type
    else:
        assert len(engine.bug_accumulator) == 0


testcases = [
    # high long
    ('''public boolean bugHighGT(long x) {
            if ((x & 0x8000000000000000L) > 0)
                return true;
            return false;
        }''', 'BIT_SIGNED_CHECK_HIGH_BIT', 1, 2, HIGH_PRIORITY),
    ('''public boolean bugHighGE(long x) {
            if ((x & 0x8000000000000000L) >= 0)
                return true;''', 'BIT_SIGNED_CHECK_HIGH_BIT', 1, 2, MEDIUM_PRIORITY),
    ('''public boolean bugHighLT(long x) {
            if ((x & 0x8000000000000000L) < 0)
                return true;''', 'BIT_SIGNED_CHECK_HIGH_BIT', 1, 2, MEDIUM_PRIORITY),
    ('''public boolean bugHighLE(long x) {
            if ((x & 0x8000000000000000L) <= 0)
                return true;''', 'BIT_SIGNED_CHECK_HIGH_BIT', 1, 2, HIGH_PRIORITY),
    # low int
    ('''public boolean bugLowGT(long x) {
                if ((x & 0x1) > 0)
                    return true;
                return false;
            }''', 'BIT_SIGNED_CHECK', 1, 2, LOW_PRIORITY),
    ('''public boolean bugLowGE(long x) {
                if ((x & 0x1) >= 0)
                    return true;''', 'BIT_SIGNED_CHECK', 1, 2, LOW_PRIORITY),
    ('''public boolean bugLowLT(long x) {
                if ((x & 0x1) < 0)
                    return true;''', 'BIT_SIGNED_CHECK', 1, 2, LOW_PRIORITY),
    ('''public boolean bugLowLE(long x) {
                if ((x & 0x1) <= 0)
                    return true;''', 'BIT_SIGNED_CHECK', 1, 2, LOW_PRIORITY),
    # high int
    ('''public boolean bugHighGT(int x) {
            if ((x & 0x80000000) > 0)
                return true;
            return false;
        }''', 'BIT_SIGNED_CHECK_HIGH_BIT', 1, 2, HIGH_PRIORITY),
    ('''public boolean bugHighGE(int x) {
            if ((x & 0x80000000) >= 0)
                return true;''', 'BIT_SIGNED_CHECK_HIGH_BIT', 1, 2, MEDIUM_PRIORITY),
    ('''public boolean bugHighLT(int x) {
            if ((x & 0x80000000) < 0)
                return true;''', 'BIT_SIGNED_CHECK_HIGH_BIT', 1, 2, MEDIUM_PRIORITY),
    ('''public boolean bugHighLE(int x) {
            if ((x & 0x80000000) <= 0)
                return true;''', 'BIT_SIGNED_CHECK_HIGH_BIT', 1, 2, HIGH_PRIORITY),

    # medium int
    ('''public boolean bugMediumGT(int x) {
            if ((x & 0x10000000) > 0)
                    return true;
                return false;
            }''', 'BIT_SIGNED_CHECK', 1, 2, MEDIUM_PRIORITY),
    ('''public boolean bugMediumGE(int x) {
                if ((x & 0x10000000) >= 0)
                    return true;''', 'BIT_SIGNED_CHECK', 1, 2, MEDIUM_PRIORITY),
    ('''public boolean bugMediumLT(int x) {
                if ((x & 0x10000000) < 0)
                    return true;''', 'BIT_SIGNED_CHECK', 1, 2, MEDIUM_PRIORITY),
    ('''public boolean bugMediumLE(int x) {
                if ((x & 0x10000000) <= 0)
                    return true;''', 'BIT_SIGNED_CHECK', 1, 2, MEDIUM_PRIORITY),
    # not
    ('''public boolean bugNotMediumMask(int x) {
            if ((x & ~0x10000000) > 0)
                return true;''', 'BIT_SIGNED_CHECK_HIGH_BIT', 1, 2, HIGH_PRIORITY),
    # DIY
    ('''public boolean DIY(int x) {
            if ((x & -10) <= 0)
                return true;''', 'BIT_SIGNED_CHECK_HIGH_BIT', 1, 2, HIGH_PRIORITY),

    ]


@pytest.mark.parametrize('patch_str,expected_warning,expected_length,expected_line_no,expected_priority', testcases)
def test_spotbugs_cases(patch_str: str, expected_warning: str, expected_length: str, expected_line_no: int,
                  expected_priority: int):
    patch = parse(patch_str, is_patch=False)
    engine = DefaultEngine([IncompatMaskDetector()])
    engine.visit([patch])
    if expected_length > 0:
        assert len(engine.bug_accumulator) == expected_length
        assert engine.bug_accumulator[0].type == expected_warning
        assert engine.bug_accumulator[0].line_no == expected_line_no
        assert engine.bug_accumulator[0].priority == expected_priority

    else:
        assert len(engine.bug_accumulator) == 0
