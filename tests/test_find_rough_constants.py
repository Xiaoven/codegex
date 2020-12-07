from rparser import parse
from patterns.detect.find_rough_constants import FindRoughConstants


class TestCntRoughConstantValue:
    def test_01(self):
        patch = parse(
            "@@ -78,8 +78,8 @@ protected VariationFunc getRandom3DShape() {\n         varFunc = VariationFuncList.getVariationFuncInstance(\"parplot2d_wf\", true);\n         varFunc.setParameter(\"use_preset\", 1);\n         varFunc.setParameter(\"preset_id\", WFFuncPresetsStore.getParPlot2DWFFuncPresets().getRandomPresetId());\n+        varFunc.setParameter(\"umin\", -3.14159265);\n+        varFunc.setParameter(\"umax\", 3.14159265);\n-        varFunc.setParameter(\"umin\", -Math.PI);\n-        varFunc.setParameter(\"umax\", Math.PI);\n         varFunc.setParameter(\"vmin\", -3);\n         varFunc.setParameter(\"vmax\", 8);\n         varFunc.setParameter(\"direct_color\", 1);")
        detector = FindRoughConstants()
        detector.visit([patch])
        assert len(detector.bug_accumulator) == 2

    def test_02(self):
        # succeed to find file when run `python -m pytest tests/ ` from command line
        # but fail when run from pycharm
        with open('tests/data/cnt_rough_constant_value.java', 'r') as f:
            content = f.read()
        if content:
            patch = parse(content)
            detector = FindRoughConstants()
            detector.visit([patch])
            assert len(detector.bug_accumulator) == 28

    # https: // github.com / alibaba / fastjson / pull / 2655 / files  # diff-16b3c16c736dce233aa4cfbdf1fce6e9485df5afc86c5434697bff31facb36d2R11
    def test_03(self):
        patch = parse(
            '''@@ -78,3 +78,3 @@ protected VariationFunc getRandom3DShape() {\n         
            private String[] jstrUnionOfRightArray = { ' [ ]", "[\"Today\"]", "[1234]", "[-0]", "[1.2333]", " [3.14e+0]",
			    " [-3.14E-0]", "[0e0]", "[true]", "[false]", "[null]", "[\"\\u1234\"]", " [{\"name\":\"test\"}]",
			    "[{}, [{}, []]]   " , "    "};"
			''')
        detector = FindRoughConstants()
        detector.visit([patch])
        assert len(detector.bug_accumulator) == 0
