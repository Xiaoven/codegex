import pytest

from codegex.models.context import Context
from codegex.utils.rparser import parse
from codegex.models.engine import DefaultEngine

params = [
    # From SpotBugs: https://github.com/spotbugs/spotbugs/blob/51e586bed98393e53559a38c1f9bd15f54514efa/spotbugsTestCases/src/java/DumbMethodInvocations.java
    ('UCF_USELESS_CONTROL_FLOW_NEXT_LINE', 'TestUselessControlFlowNextLineDetector_01.java',
     '''if (unalisedPwd != null && "".equals(unalisedPwd));
            return unalisedPwd;
    ''', 1, 1),
    # From SpotBugs: https://github.com/pfirmstone/JGDMS/commit/19723b8d66bd53761d4220fd42320d4eebbf204d
    ('UCF_USELESS_CONTROL_FLOW_NEXT_LINE', 'TestUselessControlFlowNextLineDetector_02.java',
     '''if (type != null && type.isInstance(result)) ;
    ''', 1, 1),
    # DIY
    ('UCF_USELESS_CONTROL_FLOW_NEXT_LINE', 'TestUselessControlFlowNextLineDetector_03.java',
     '''if(false){
            System.out.println("false");
        }else if(false);
            System.out.println("false");
        System.out.println("true");
    ''', 1, 3),
    ('UCF_USELESS_CONTROL_FLOW_NEXT_LINE', 'TestUselessControlFlowNextLineDetector_04.java',
     "if(a>0) return (a%2==0);", 0, 0),
    # ('UCF_USELESS_CONTROL_FLOW_NEXT_LINE', 'TestUselessControlFlowNextLineDetector_05.java',
    #  "while (count-- > 0);", 1, 1),  # abort this since it may be a part of do-while loop
    ('UCF_USELESS_CONTROL_FLOW_NEXT_LINE', 'TestUselessControlFlowNextLineDetector_06.java',
     "for(char c : chars);", 1, 1),
    ('UCF_USELESS_CONTROL_FLOW_NEXT_LINE', 'TestUselessControlFlowNextLineDetector_07.java',
     "} while ((ci = ci.getSuperClass()) != null);", 0, 0),

]


@pytest.mark.parametrize('pattern_type,file_name,patch_str,expected_length,line_no', params)
def test(pattern_type: str, file_name: str, patch_str: str, expected_length: int, line_no: int):
    patch = parse(patch_str, False)
    patch.name = file_name
    engine = DefaultEngine(Context(), included_filter=('UselessControlFlowNextLineDetector',))
    engine.visit(patch)
    if expected_length > 0:
        assert len(engine.bug_accumulator) == expected_length
        assert engine.bug_accumulator[0].line_no == line_no
        assert engine.bug_accumulator[0].type == pattern_type
    else:
        assert len(engine.bug_accumulator) == 0

