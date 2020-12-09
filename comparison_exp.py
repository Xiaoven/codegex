import os
import time
from os import path
from subprocess import check_output
import re
from datetime import datetime

from patterns.detect.dont_catch_illegal_monitor_state_exception import DontCatchIllegalMonitorStateException
from patterns.detect.dumb_methods import DumbMethods
from patterns.detect.find_finalize_invocations import FindFinalizeInvocations
from patterns.detect.find_ref_comparison import FindRefComparison
from patterns.detect.find_rough_constants import FindRoughConstants
from patterns.detect.find_unrelated_types_in_generic_container import FindUnrelatedTypesInGenericContainer
from patterns.detect.format_string_checker import FormatStringChecker
from patterns.detect.incompat_mask import BitSignedCheckAndBitAndZZ
from patterns.detect.infinite_recursive_loop import InfiniteRecursiveLoop
from patterns.detect.inheritance_unsafe_get_resource import InheritanceUnsafeGetResource
from patterns.detect.method_return_check import MethodReturnCheck
from patterns.detect.naming import Naming
from patterns.detect.serializable_idiom import SerializableIdiom
from patterns.detect.static_calendar_detector import StaticCalendarDetector
from rparser import parse

BASE_PATH = '/home/xiaowen/Project/rbugs_experiments/github-repos'
LOG_PATH = 'comparison_exp'

TASK_MAIN = 'task_main'
TASK_TEST = 'task_test'

JAVA_FILE_PATTERN = re.compile(r'(.+?)/src/(main|test)/java/')

# Run collect_bug_pattern.py and copy the "[Detectors]" string
DETECTORS = [BitSignedCheckAndBitAndZZ(), InheritanceUnsafeGetResource(), StaticCalendarDetector(),
             MethodReturnCheck(), InfiniteRecursiveLoop(), FindRoughConstants(), FindRefComparison(),
             Naming(), DontCatchIllegalMonitorStateException(), FindFinalizeInvocations(),
             SerializableIdiom(), FindUnrelatedTypesInGenericContainer(), DumbMethods(), FormatStringChecker()]


def empty_file(file_path: str):
    open(file_path, 'w').close()


def append_file(file_path: str, content: str):
    with open(file_path, 'a') as f:
        f.write(content)


def write_file(file_path: str, content: str):
    with open(file_path, 'w') as f:
        f.write(content)


def exec_task(file_dict: dict):
    bug_instance_dict = dict()

    for subproject, file_list in file_dict.items():
        # generate patch set
        patchset = []
        for file_path in file_list:
            with open(file_path, 'r') as f:
                patch = parse(f.read(), is_patch=False)
                patch.name = file_path
                patchset.append(patch)

        # run detectors
        if not patchset:
            continue

        bug_instances = list()
        for detector in DETECTORS:
            detector.visit(patchset)
            if detector.bug_accumulator:
                bug_instances.extend(detector.bug_accumulator)

        bug_instance_dict[subproject] = bug_instances
    return bug_instance_dict


def detect_project(project_name: str, tasks=(TASK_MAIN, TASK_TEST)):
    # get java files
    source_paths = dict()
    test_paths = dict()
    other_paths = list()
    project_path = path.join(BASE_PATH, project_name)
    output = check_output(['find', project_path, '-name', '*.java']).decode('utf-8')
    if not output.strip():
        return
    for file_path in output.splitlines():
        m = JAVA_FILE_PATTERN.match(file_path)
        if m:
            g = m.groups()

            if g[1] == 'main' in file_path:
                tmp_paths = source_paths.get(g[0], list())
                tmp_paths.append(file_path)
                source_paths[g[0]] = tmp_paths
            elif g[1] == 'test' in file_path:
                tmp_paths = source_paths.get(g[0], list())
                tmp_paths.append(file_path)
                test_paths[g[0]] = tmp_paths
            else:
                other_paths.append(file_path)

    log_dir = path.join(LOG_PATH, project_name)
    os.makedirs(log_dir, exist_ok=True)
    logfile = path.join(log_dir, 'detect.log')
    empty_file(logfile)
    if other_paths:
        append_file(logfile, '------------------------- Unknown Java Files -------------------------\n'
                    + '\n'.join(other_paths) + '\n')

    unknown_tasks = list()
    for task in tasks:
        bug_ins_dict = dict()
        log_file_name = ''
        if task == TASK_MAIN:
            append_file(logfile, '------------------------- Execute Task Main -------------------------\n')
            bug_ins_dict = exec_task(source_paths)
            log_file_name = 'main.xml'
        elif task == TASK_TEST:
            append_file(logfile, '------------------------- Execute Task Test -------------------------\n')
            bug_ins_dict = exec_task(test_paths)
            log_file_name = 'test.xml'
        else:
            unknown_tasks.append(task)

        # write reports
        for subproject, bug_instances in bug_ins_dict.items():
            if bug_instances:
                report_path = subproject.replace(BASE_PATH, log_dir)
                os.makedirs(report_path, exist_ok=True)
                report_path = path.join(report_path, log_file_name)
                content = str()
                for ins in bug_instances:
                    content += f'{ins.file_name},{ins.type},{ins.line_no}\n'
                write_file(report_path, content)
                append_file(logfile, f'Found {len(bug_instances)} violations: f{report_path}\n')

    if unknown_tasks:
        append_file(logfile, '------------------------- Unknown Tasks -------------------------\n'
                    + '\n'.join(unknown_tasks) + '\n')


if __name__ == '__main__':
    # for project_name in os.listdir(BASE_PATH):
    start = datetime.now()
    detect_project('elasticsearch')
    end = datetime.now()
    diff = end - start
    elapsed_ms = (diff.days * 86400000) + (diff.seconds * 1000) + (diff.microseconds / 1000)
    print('elapsed_ms', elapsed_ms)

