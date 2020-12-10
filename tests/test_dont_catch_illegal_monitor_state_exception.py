import pytest

from patterns.detectors import DefaultEngine
from rparser import parse
from patterns.detect.dont_catch_illegal_monitor_state_exception import DontCatchIllegalMonitorStateException

params = [
    (True, DontCatchIllegalMonitorStateException(), 'IMSE_DONT_CATCH_IMSE', 'Fake.java',
           '''@@ -146,11 +147,7 @@ public void serviceAdded(ServiceEvent se) {
             log.debug("Service added: {}", se.getInfo().toString());
             // notify the client when a service is added.
             synchronized (client) {
+                try {
+                    client.notifyAll();
+                } catch (java.lang.IllegalMonitorStateException imse) {
+                    log.error("Error notifying waiting listeners: {}", imse.getCause());
+                }
-                client.notifyAll();
             }
         }''',
           1, 152),
    (False, DontCatchIllegalMonitorStateException(), 'IMSE_DONT_CATCH_IMSE', 'Fake.java',
        '''
        } catch (IOException io, 
                    java.lang.IllegalMonitorStateException imse) {
                        log.error("Error notifying waiting listeners: {}", imse.getCause());
                }
        ''', 1, 3),
]


@pytest.mark.parametrize('is_patch,detector,pattern_type,file_name,patch_str,expected_length,line_no', params)
def test(is_patch: bool, detector, pattern_type: str, file_name: str, patch_str: str, expected_length: int,
         line_no: int):
    patch = parse(patch_str, is_patch)
    patch.name = file_name
    engine = DefaultEngine([detector])
    engine.visit([patch])
    if expected_length > 0:
        assert len(engine.bug_accumulator) == expected_length
        assert engine.bug_accumulator[0].line_no == line_no
        assert engine.bug_accumulator[0].type == pattern_type
    else:
        assert len(engine.bug_accumulator) == 0