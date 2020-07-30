from parser import Patch
from patterns.detect.cnt_rough_constant_value import FindRoughConstants

if __name__ == '__main__':
    filepath = 'test_data/cnt_rough_constant_value.java'
    content = None
    with open(filepath, 'r') as f:
        content = f.read()

    if content:
        patch = Patch()
        patch.parse(content)
        detector = FindRoughConstants()
        detector.visit([patch])
        detector.report()