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

    # From other repository: https://github.com/universAAL/middleware/commit/daf0a4ca23297f08713e722d5f2fd891699aa95f
    def test_DM_STRING_VOID_CTOR_01(self):
        patch = Patch()
        patch.name = "SimpleProperties.java"
        patch.parse(
            '''@@ -1153,7 +1153,7 @@ public String toStringRecursive(String prefix, boolean prefixAtStart,
            if (visitedElements == null)
                visitedElements = new Hashtable();
        
            String s = new String();
            if (prefixAtStart)
                s += prefix;
            s += this.getClass().getName() + "\n";''')
        detector = DumbMethods()
        detector.visit([patch])
        assert len(detector.bug_accumulator) == 1
        bugins = detector.bug_accumulator[0]
        assert bugins.type == 'DM_STRING_VOID_CTOR'
        assert bugins.line_no == 1156

    # DIY
    def test_DM_STRING_VOID_CTOR_02(self):
        patch = Patch()
        patch.name = "Fake.java"
        patch.parse(
            '''@@ -1153,7 +1153,7 @@ public String toStringRecursive(String prefix, boolean prefixAtStart,
            String s = new String(  );
            ''')
        detector = DumbMethods()
        detector.visit([patch])
        assert len(detector.bug_accumulator) == 1
        bugins = detector.bug_accumulator[0]
        assert bugins.type == 'DM_STRING_VOID_CTOR'
        assert bugins.line_no == 1153

    # From other repository: https://github.com/test-pki/dogtag-pki/commit/a4db0f39e257950a5c89203452c1184c7080e5bd#diff-a73d367ef2afa1ab0151ca0df88ac96d
    def test_DM_STRING_CTOR_01(self):
        patch = Patch()
        patch.name = "SimpleProperties.java"
        patch.parse(
            "@@ -191,6 +191,7 @@ public synchronized void load(InputStream inStream) throws IOException {  \n"
            "   if (whiteSpaceChars.indexOf(nextLine.charAt(startIndex)) == -1)\n"
            " break;\n"
            "   nextLine = nextLine.substring(startIndex, nextLine.length());\n"
            "+     line = new String(loppedLine + nextLine);\n"
            "   }\n"
            " // Find start of key\n"
            " int len = line.length();")
        detector = DumbMethods()
        detector.visit([patch])
        assert len(detector.bug_accumulator) == 1
        bugins = detector.bug_accumulator[0]
        assert bugins.type == 'DM_STRING_CTOR'
        assert bugins.line_no == 194

    # From other repository: https://github.com/HighTechRedneck42/JMRI/commit/e0f5ae298a1bad0b7abca627d7ab15e2b6d2fd69
    def test_DM_STRING_CTOR_02(self):
        patch = Patch()
        patch.name = "DCCppSimulatorAdapter.java"
        patch.parse('''@@ -467,7 +467,7 @@ private void generateRandomSensorReply() {
                        Random valueGenerator = new Random();
                        int value = valueGenerator.nextInt(2); // Generate state value betweeon 0 and 1
                    
                        String reply = new String((value == 1 ? "Q " : "q ")+ Integer.toString(sensorNum));''')
        detector = DumbMethods()
        detector.visit([patch])
        assert len(detector.bug_accumulator) == 1
        bugins = detector.bug_accumulator[0]
        assert bugins.type == 'DM_STRING_CTOR'
        assert bugins.line_no == 470

    # From other repository: https://github.com/exedio/persistence/commit/cb142171ce28704f463dfb2b95307ac203d3fd39
    def test_DM_STRING_CTOR_03(self):
        patch = Patch()
        patch.name = "ReserializeTest.java"
        patch.parse('''@@ -23,10 +23,12 @@
                    import static org.junit.Assert.assertNotSame;
                    import static org.junit.Assert.assertSame;
                    
                    import edu.umd.cs.findbugs.annotations.SuppressFBWarnings;
                    import org.junit.Test;
                    
                    public class ReserializeTest
                    {
                        @SuppressFBWarnings("DM_STRING_CTOR")
                        @Test public void testIt()
                        {
                            final String[] original = new String[]{new String("hallo"), new String("hallo")};''')
        detector = DumbMethods()
        detector.visit([patch])
        assert len(detector.bug_accumulator) == 1
        bugins = detector.bug_accumulator[0]
        assert bugins.type == 'DM_STRING_CTOR'
        assert bugins.line_no == 34

