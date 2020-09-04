import json
import glob

from rparser import Patch
from patterns.detect.dumb_methods import DmRunFinalizerOnExit
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
    root = 'Java'
    paths = glob.glob(f'{root}/**/*.json', recursive=True)
    for p in paths:
        patchset = get_modified_patchset(p)
        if patchset:
            detector = DmRunFinalizerOnExit() # run different detector on Java pull requests
            detector.visit(patchset)
            if detector.bug_accumulator:
                logger.info(p)
            detector.report()
