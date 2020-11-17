import pytest

from rparser import parse
from patterns.detect.imse_dont_catch_imse import DontCatchIllegalMonitorStateException

params = [(True, DontCatchIllegalMonitorStateException(), 'IMSE_DONT_CATCH_IMSE', 'Fake.java',
           "@@ -146,11 +147,7 @@ public void serviceAdded(ServiceEvent se) {\n             log.debug(\"Service added: {}\", se.getInfo().toString());\n             // notify the client when a service is added.\n             synchronized (client) {\n+                try {\n+                    client.notifyAll();\n+                } catch (java.lang.IllegalMonitorStateException imse) {\n+                    log.error(\"Error notifying waiting listeners: {}\", imse.getCause());\n+                }\n-                client.notifyAll();\n             }\n         }\n",
           1, 152),
          ]


@pytest.mark.parametrize('is_patch,detector,pattern_type,file_name,patch_str,expected_length,line_no', params)
def test(is_patch: bool, detector, pattern_type: str, file_name: str, patch_str: str, expected_length: int,
         line_no: int):
    patch = parse(patch_str, is_patch)
    patch.name = file_name
    detector.visit([patch])
    if expected_length > 0:
        assert len(detector.bug_accumulator) == expected_length
        assert detector.bug_accumulator[0].line_no == line_no
        assert detector.bug_accumulator[0].type == pattern_type
    else:
        assert len(detector.bug_accumulator) == 0
