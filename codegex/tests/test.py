import pytest
from typing import List

from codegex.models.context import Context
from codegex.models.engine import DefaultEngine
from codegex.utils.rparser import parse

"""
expectations format: {type: [line no1, line no2, ...]}
"""

# detector name
d_num_ctor = 'NumberCTORDetector'
d_fp_ctor = 'FPNumberCTORDetector'
d_boxed_parsing = 'BoxedPrimitiveForParsingDetector'

# pattern type
p_num_ctor = 'DM_NUMBER_CTOR'
p_fp_ctor = 'DM_FP_NUMBER_CTOR'
p_boxed_parsing = 'DM_BOXED_PRIMITIVE_FOR_PARSING'


cases = [
    ([d_num_ctor, d_fp_ctor], 'test_01',
     '''Object[] params = new Object[]{new Integer(initialK) ,new Integer(seedFragmentLength),
                new Float(seedRmsdCutoff),
                new Integer(fragmentLength),
                new Integer(diagonalDistance), new Integer(diagonalDistance2), new Float(fragmentMiniDistance),
                new Integer(angleDiff),
                new Float(fragCompat), new Integer(maxrefine),
                new Boolean(reduceInitialFragments), new Double(joinRMSCutoff), new Boolean(joinPlo),
                new Boolean(doAngleCheck), new Boolean(doDistanceCheck), new Boolean(doRMSCheck),
                new Boolean(doDensityCheck), new Float(densityCutoff), new Float(create_co), new Integer(maxIter),
                new Float(gapOpen), new Float(gapExtension), new Integer(permutationSize), new Float(evalCutoff)};''',
     False, {p_num_ctor: 1, p_fp_ctor: 2}),
    ([d_num_ctor, d_boxed_parsing], 'test_02',
     'final long timeInMillis = new Long(str);\n'
     'int start = Integer.valueOf(m.group(3));\n'
     'int offset = Integer.valueOf(params[0]);\n', False, {p_num_ctor: 1, p_boxed_parsing: [1, 2, 3]})
]


@pytest.mark.parametrize('filters,test_name,patch_str,is_patch,expectations', cases)
def test(filters: List[str], test_name: str, patch_str: str, is_patch: bool, expectations: dict):
    patch = parse(patch_str, is_patch)
    patch.name = test_name
    engine = DefaultEngine(Context(), included_filter=filters)
    engine.visit(patch)

    for instance in engine.bug_accumulator:
        target = (instance.type, instance.line_no)
        if instance.type in expectations:
            if isinstance(expectations[instance.type], int) and instance.line_no == expectations[instance.type]:
                expectations.pop(instance.type)
            elif instance.line_no in expectations[instance.type]:
                expectations[instance.type].remove(instance.line_no)
                if not expectations[instance.type]:
                    expectations.pop(instance.type)
    assert not expectations
