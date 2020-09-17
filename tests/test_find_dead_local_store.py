from patterns.detect.find_dead_local_stores import FindDeadLocalStoreMethods
from rparser import Patch


class TestFindDeadLocalStore:

    # From Findbugs repo:findbugs/findbugsTestCases/src/java/sfBugs/Bug1911620.java
    def test_FIND_LOCAL_INCREMENT_IN_RETURN_01(self):
        patch = Patch()
        patch.name = "Fake.java"
        patch.parse(
            '@@ -19,18 +37,24 @@ public long getLongWithDLS(String longStr) {\n     }\n \n     public long getLongMinus1_2(String longStr) {\n-        long l = Long.valueOf(longStr);\n+        long l = Long.parseLong(longStr);\n         --l;\n         return l;\n     }\n \n     public long getLongMinus2(String longStr) {\n-        long l = Long.valueOf(longStr);\n+        long l = Long.parseLong(longStr);\n         return l - 2;\n     }\n \n     public int getIntMinus1(String intStr) {\n-        int i = Integer.valueOf(intStr);\n+        int i = Integer.parseInt(intStr);\n         return --i;\n     }\n+    \n+    @ExpectWarning(\"DLS_DEAD_LOCAL_INCREMENT_IN_RETURN\")\n+    public int getIntMinus1Bad(String intStr) {\n+        int i = Integer.parseInt(intStr);\n+        return i--;\n+    }\n }'
        )
        '''
        source patch is too long to display
        core code is 
        +    @ExpectWarning("DLS_DEAD_LOCAL_INCREMENT_IN_RETURN")
        +    public int getIntMinus1Bad(String intStr) {
        +       int i = Integer.parseInt(intStr);
        +       return i--;
         }
        '''
        detector = FindDeadLocalStoreMethods()
        detector.visit([patch])
        detector.report()
        assert len(detector.bug_accumulator) == 1

    # DIY idea From other repo:https://github.com/sidkuma24/Software-Engineering/blob/19d738b11f5ed3d9d2c187cd6ffe08bacf3e69cd/Assignment-2/findbugs-test_cases/correctness_related_errors/example5.java
    def test_FIND_LOCAL_INCREMENT_IN_RETURN_02(self):
        patch = Patch()
        patch.name = "Fake.java"
        patch.parse('@@ -1,1 +1,4 @@ public class Main{\n'
                    '+                    static int nextNumber(int i){\n      '
                    '+                        return primes[i]++;//useless increment\n'
                    '+ }\n')
        detector = FindDeadLocalStoreMethods()
        detector.visit([patch])
        detector.report()
        assert len(detector.bug_accumulator) == 0

    # DIY
    def test_FIND_LOCAL_INCREMENT_IN_RETURN_03(self):
        patch = Patch()
        patch.name = "Fake.java"
        patch.parse('@@ -1,1 +1,4 @@ public class Main{\n'
                    '+                    static int nextNumber(int $num123){\n      '
                    '+                        return $num123++;//useless increment\n'
                    '+  }\n')
        detector = FindDeadLocalStoreMethods()
        detector.visit([patch])
        detector.report()
        assert len(detector.bug_accumulator) == 1
