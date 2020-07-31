import json
import glob

from parser import Patch
from patterns.detect.cnt_rough_constant_value import FindRoughConstants
from patterns.utils import logger


def get_modified_patchset(path):
    patchset = []
    with open(path, 'r') as jf:
        jfile = json.load(jf)
        for file in jfile:
            name = file['filename']

            if name.endswith('.java'):
                if 'patch' in file and file['status'] != 'removed':
                    patch = Patch()
                    patch.name = name
                    patch.type = file['status']
                    patch.parse(file['patch'])
                    patchset.append(patch)
    return patchset


if __name__ == '__main__':
    root = 'PR_database/Java'
    paths = glob.glob(f'{root}/**/*.json', recursive=True)
    for p in paths:
        patchset = get_modified_patchset(p)
        if patchset:
            detector = FindRoughConstants()
            detector.visit(patchset)
            if detector.bug_accumulator:
                logger.info(p)
            detector.report()
