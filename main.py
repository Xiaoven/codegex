import json
import glob

from patterns.detect.cnt_rough_constant_value import FindRoughConstants
from patterns.detect.find_finalize_invocations import FindFinalizeInvocations
from patterns.detect.find_ref_comparison import FindRefComparison
from patterns.detect.find_unrelated_types_in_generic_container import FindUnrelatedTypesInGenericContainer
from patterns.detect.format_string_checker import FormatStringChecker
from patterns.detect.imse_dont_catch_imse import DontCatchIllegalMonitorStateException
from patterns.detect.infinite_recursive_loop import InfiniteRecursiveLoop
from patterns.detect.inheritance_unsafe_get_resource import InheritanceUnsafeGetResource
from patterns.detect.naming import Naming
from patterns.detect.serializable_idiom import SerializableIdiom
from patterns.detect.static_calendar_detector import StaticCalendarDetector
from rparser import Patch, parse
from patterns.detect.dumb_methods import DumbMethods
from patterns.utils import logger, logger_add, TRACE

# 25 patterns
DETECTORS = [FindRoughConstants(), DumbMethods(), FindFinalizeInvocations(),
             FindRefComparison(), FindUnrelatedTypesInGenericContainer(), FormatStringChecker(),
             DontCatchIllegalMonitorStateException(), InfiniteRecursiveLoop(), InheritanceUnsafeGetResource(),
             Naming(), SerializableIdiom(), StaticCalendarDetector()]


def get_modified_patchset(path):
    patchset = []
    with open(path, 'r') as jf:
        jfile = json.load(jf)
        for file in jfile:
            name = file['filename']

            if name.endswith('.java'):
                if 'patch' in file and file['status'] != 'removed':
                    patch = parse(file['patch'])
                    patch.name = name
                    patch.type = file['status']

                    patchset.append(patch)
    return patchset


if __name__ == '__main__':
    root = 'Java'
    paths = glob.glob(f'{root}/**/*.json', recursive=True)

    # logger name
    logger.remove(TRACE)
    cnt = 1
    trace = logger_add('out/', f'{cnt}.log')
    has_bug = False

    for p in paths:
        if has_bug:
            logger.remove(trace)
            cnt += 1
            trace = logger_add('out/', f'{cnt}.log')
            has_bug = False

        patchset = get_modified_patchset(p)
        if patchset:
            for detector in DETECTORS:
                detector.visit(patchset)
                if detector.bug_accumulator:
                    detector.report()
                    has_bug = True

        if has_bug:
            logger.info(p)
