from patterns.detect.find_finalize_invocations import FiExplicitInvocation
from rparser import Patch
from patterns.detect.dumb_methods import DumbMethods


class TestFinalizer:
    def test_DM_RUN_FINALIZERS_ON_EXIT_01(self):
        patch = Patch()
        patch.name = "StdEntropyDecoder.java"
        patch.parse("@@ -622,7 +622,7 @@ public StdEntropyDecoder(CodedCBlkDataSrcDec src, DecoderSpecs decSpec,\n"
                    "         if (DO_TIMING) {\n"
                    "             time = new long[src.getNumComps()];\n"
                    "             // If we are timing make sure that 'finalize' gets called.\n"
                    "+            System.runFinalizersOnExit(true);\n"
                    "         }\n \n"
                    "         // Initialize internal variables")
        detector = DumbMethods()
        detector.visit([patch])
        assert len(detector.bug_accumulator) == 1
        bugins = detector.bug_accumulator[0]
        assert bugins.type == 'DM_RUN_FINALIZERS_ON_EXIT'
        assert bugins.line_no == 625

    # From other repository: https://github.com/jenkinsci/android-emulator-plugin/commit/0e104f3f0fc18505c13932fccd3b2297e78db694#diff-238b9af87181bb379670392cdb1dcd6bL173
    def test_DMI_RANDOM_USED_ONLY_ONCE_01(self):
        patch = Patch()
        patch.name = "MonkeyBuilder.java"
        patch.parse("@@ -166,11 +167,10 @@ private static void addArguments(String parameters, String flag, StringBuilder a\n"
                    "        }\n"
                    "    }\n\n"
                    "-    @SuppressFBWarnings(\"DMI_RANDOM_USED_ONLY_ONCE\")\n"
                    "    private static long parseSeed(String seed) {\n"
                    "        long seedValue;\n"
                    "        if (\"random\".equals(seed)) {\n"
                    "            seedValue = new Random().nextLong();\n"
                    "        } else if (\"timestamp\".equals(seed)) {\n")
        detector = DumbMethods()
        detector.visit([patch])
        detector = DumbMethods()
        detector.visit([patch])
        assert len(detector.bug_accumulator) == 1
        bugins = detector.bug_accumulator[0]
        assert bugins.type == 'DMI_RANDOM_USED_ONLY_ONCE'
        assert bugins.line_no == 173

    # From other repository: https://github.com/adaptris/interlok/commit/8dd32e9b89a4b17662faa7ca986756f3cc348cc7#diff-1e0469ce35c1d148418525088df452a2L405
    def test_DMI_RANDOM_USED_ONLY_ONCE_02(self):
        patch = Patch()
        patch.name = "MonkeyBuilder.java"
        patch.parse('''@@ -393,15 +396,13 @@ protected synchronized void sendMessageLifecycleEvent(AdaptrisMessage msg) {

  private GenericObjectPool<Worker> createObjectPool() {
    GenericObjectPool<Worker> pool = new GenericObjectPool<>(new WorkerFactory());
-    long lifetime = threadLifetimeMs();
    pool.setMaxTotal(poolSize());
    pool.setMinIdle(minIdle());
    pool.setMaxIdle(maxIdle());
    pool.setMaxWaitMillis(-1L);
    pool.setBlockWhenExhausted(true);
+    pool.setMinEvictableIdleTimeMillis(threadLifetimeMs());
+    pool.setTimeBetweenEvictionRunsMillis(threadLifetimeMs() + new Random(threadLifetimeMs()).nextLong());
+    return pool;''')
        detector = DumbMethods()
        detector.visit([patch])
        detector = DumbMethods()
        detector.visit([patch])
        assert len(detector.bug_accumulator) == 1
        bugins = detector.bug_accumulator[0]
        assert bugins.type == 'DMI_RANDOM_USED_ONLY_ONCE'
        assert bugins.line_no == 405

    # From other repository: https://github.com/adaptris/interlok/commit/8dd32e9b89a4b17662faa7ca986756f3cc348cc7#diff-766b5e25592ad321e107f1f856d8a08bL102
    def test_DMI_RANDOM_USED_ONLY_ONCE_03(self):
        patch = Patch()
        patch.name = "MonkeyBuilder.java"
        patch.parse('''@@ -99,7 +98,8 @@ private Service cloneService(Service original) throws Exception {
    pool.setMaxWait(-1L);
    pool.setWhenExhaustedAction(org.apache.commons.pool.impl.GenericObjectPool.WHEN_EXHAUSTED_BLOCK);
    pool.setMinEvictableIdleTimeMillis(EVICT_RUN);
    pool.setTimeBetweenEvictionRunsMillis(EVICT_RUN + new Random(EVICT_RUN).nextLong());''')
        detector = DumbMethods()
        detector.visit([patch])
        detector = DumbMethods()
        detector.visit([patch])
        assert len(detector.bug_accumulator) == 1
        bugins = detector.bug_accumulator[0]
        assert bugins.type == 'DMI_RANDOM_USED_ONLY_ONCE'
        assert bugins.line_no == 101

    # DIY
    def test_DMI_RANDOM_USED_ONLY_ONCE_04(self):
        patch = Patch()
        patch.name = "MonkeyBuilder.java"
        patch.parse("@@ -166,11 +167,10 @@ private static void addArguments(String parameters, String flag, StringBuilder a\n"
                    "        }\n"
                    "    }\n\n"
                    "-    @SuppressFBWarnings(\"DMI_RANDOM_USED_ONLY_ONCE\")\n"
                    "    private static long parseSeed(String seed) {\n"
                    "        long seedValue;\n"
                    "        if (\"random\".equals(seed)) {\n"
                    "            seedValue = new java.util.Random().nextLong();\n"
                    "        } else if (\"timestamp\".equals(seed)) {\n")
        detector = DumbMethods()
        detector.visit([patch])
        detector = DumbMethods()
        detector.visit([patch])
        assert len(detector.bug_accumulator) == 1
        bugins = detector.bug_accumulator[0]
        assert bugins.type == 'DMI_RANDOM_USED_ONLY_ONCE'
        assert bugins.line_no == 173