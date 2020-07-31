import pytest

from parser import Patch
from patterns.detect.cnt_rough_constant_value import FindRoughConstants

class TestCntRoughConstantValue:
    def test_01(self):
        patch = Patch()
        patch.parse("@@ -78,8 +78,8 @@ protected VariationFunc getRandom3DShape() {\n         varFunc = VariationFuncList.getVariationFuncInstance(\"parplot2d_wf\", true);\n         varFunc.setParameter(\"use_preset\", 1);\n         varFunc.setParameter(\"preset_id\", WFFuncPresetsStore.getParPlot2DWFFuncPresets().getRandomPresetId());\n+        varFunc.setParameter(\"umin\", -3.14159265);\n+        varFunc.setParameter(\"umax\", 3.14159265);\n-        varFunc.setParameter(\"umin\", -Math.PI);\n-        varFunc.setParameter(\"umax\", Math.PI);\n         varFunc.setParameter(\"vmin\", -3);\n         varFunc.setParameter(\"vmax\", 8);\n         varFunc.setParameter(\"direct_color\", 1);")
        detector = FindRoughConstants()
        detector.visit([patch])
        assert len(detector.bug_accumulator) == 2

    def test_02(self):
        with open('data/cnt_rough_constant_value.java', 'r') as f:
            content = f.read()
        if content:
            patch = Patch()
            patch.parse(content)
            detector = FindRoughConstants()
            detector.visit([patch])
            assert len(detector.bug_accumulator) == 28


if __name__ == '__main__':
    pytest.main(['-q', 'test_cnt_rough_constant_value.py'])