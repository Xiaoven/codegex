import pytest

from parser import Patch
from patterns.detect.imse_dont_catch_imse import DontCatchIllegalMonitorStateException

class TestImseDontCatchImse:
    def test_01(self):
        patch = Patch()
        patch.parse("@@ -146,11 +147,7 @@ public void serviceAdded(ServiceEvent se) {\n             log.debug(\"Service added: {}\", se.getInfo().toString());\n             // notify the client when a service is added.\n             synchronized (client) {\n+                try {\n+                    client.notifyAll();\n+                } catch (java.lang.IllegalMonitorStateException imse) {\n+                    log.error(\"Error notifying waiting listeners: {}\", imse.getCause());\n+                }\n-                client.notifyAll();\n             }\n         }\n")
        detector = DontCatchIllegalMonitorStateException()
        detector.visit([patch])
        assert len(detector.bug_accumulator) == 1

if __name__ == '__main__':
    pytest.main(['-q', 'test_imse_dont_catch_imse.py'])