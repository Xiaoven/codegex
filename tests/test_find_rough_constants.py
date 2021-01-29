from patterns.models.context import Context
from patterns.models.engine import DefaultEngine
from rparser import parse


class TestCntRoughConstantValue:
    def test_01(self):
        patch = parse("@@ -78,8 +78,8 @@ protected VariationFunc getRandom3DShape() {\n         varFunc = VariationFuncList.getVariationFuncInstance(\"parplot2d_wf\", true);\n         varFunc.setParameter(\"use_preset\", 1);\n         varFunc.setParameter(\"preset_id\", WFFuncPresetsStore.getParPlot2DWFFuncPresets().getRandomPresetId());\n+        varFunc.setParameter(\"umin\", -3.14159265);\n+        varFunc.setParameter(\"umax\", 3.14159265);\n-        varFunc.setParameter(\"umin\", -Math.PI);\n-        varFunc.setParameter(\"umax\", Math.PI);\n         varFunc.setParameter(\"vmin\", -3);\n         varFunc.setParameter(\"vmax\", 8);\n         varFunc.setParameter(\"direct_color\", 1);")
        engine = DefaultEngine(Context(), included_filter=['FindRoughConstantsDetector'])
        engine.visit(patch)
        assert len(engine.bug_accumulator) == 2

    def test_02(self):
        # succeed to find file when run `python -m pytest tests/ ` from command line
        # but fail when run from pycharm
        with open('tests/data/cnt_rough_constant_value.java', 'r') as f:
            content = f.read()
        if content:
            patch = parse(content)
            engine = DefaultEngine(Context(), included_filter=['FindRoughConstantsDetector'])
            engine.visit(patch)
            assert len(engine.bug_accumulator) == 28