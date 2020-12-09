import os
from os import path
from subprocess import check_output
import re
from datetime import datetime

from patterns.detect.dont_catch_illegal_monitor_state_exception import DontCatchIllegalMonitorStateException
from patterns.detect.dumb_methods import FinalizerOnExitDetector, RandomOnceDetector, RandomD2IDetector, \
    StringCtorDetector
from patterns.detect.find_finalize_invocations import ExplicitInvDetector, PublicAccessDetector
from patterns.detect.find_ref_comparison import EqualityDetector, CalToNullDetector
from patterns.detect.find_rough_constants import FindRoughConstantsDetector
from patterns.detect.find_unrelated_types_in_generic_container import RemoveAllDetector, VacuousSelfCallDetector, \
    NotContainThemselvesDetector
from patterns.detect.format_string_checker import NewLineDetector
from patterns.detect.incompat_mask import BitSignedCheck, BitSignedCheckAndBitAndZZDetector
from patterns.detect.infinite_recursive_loop import CollectionAddItselfDetector
from patterns.detect.inheritance_unsafe_get_resource import GetResourceDetector
from patterns.detect.method_return_check import NotThrowDetector
from patterns.detect.naming import SimpleNameDetector1, SimpleNameDetector2
from patterns.detect.serializable_idiom import DefSerialVersionID, DefReadResolveMethod
from patterns.detect.static_calendar_detector import StaticDateFormatDetector
from patterns.detectors import DefaultEngine
from rparser import parse
from timer import Timer

BASE_PATH = '/home/xiaowen/Project/rbugs_experiments/github-repos'
LOG_PATH = 'comparison_exp'

TASK_MAIN = 'task_main'
TASK_TEST = 'task_test'

JAVA_FILE_PATTERN = re.compile(r'(.+?)/src/(main|test)/java/')

# Run collect_bug_pattern.py and copy the "[Detectors]" string
DETECTORS = [BitSignedCheck(), BitSignedCheckAndBitAndZZDetector(), GetResourceDetector(), StaticDateFormatDetector(),
             NotThrowDetector(), CollectionAddItselfDetector(), FindRoughConstantsDetector(), EqualityDetector(),
             CalToNullDetector(), SimpleNameDetector1(), SimpleNameDetector2(), DontCatchIllegalMonitorStateException(),
             ExplicitInvDetector(), PublicAccessDetector(), DefSerialVersionID(), DefReadResolveMethod(),
             RemoveAllDetector(), VacuousSelfCallDetector(), NotContainThemselvesDetector(), FinalizerOnExitDetector(),
             RandomOnceDetector(), RandomD2IDetector(), StringCtorDetector(), NewLineDetector()
             ]


def empty_file(file_path: str):
    t = Timer(name='io', logger=None)
    t.start()
    open(file_path, 'w').close()
    t.stop()


def append_file(file_path: str, content: str):
    t = Timer(name='io', logger=None)
    t.start()
    with open(file_path, 'a') as f:
        f.write(content)
    t.stop()


def write_file(file_path: str, content: str):
    t = Timer(name='io', logger=None)
    t.start()
    with open(file_path, 'w') as f:
        f.write(content)
    t.stop()


def exec_task(file_dict: dict):
    bug_instance_dict = dict()
    engine = DefaultEngine(DETECTORS)

    for subproject, file_list in file_dict.items():
        t = Timer(name='parsing', logger=None)
        t.start()
        # generate patch set
        patchset = []
        for file_path in file_list:
            with open(file_path, 'r') as f:
                patch = parse(f.read(), is_patch=False)
                patch.name = file_path
                patchset.append(patch)
        t.stop()

        # run detectors
        if not patchset:
            continue

        t = Timer(name='detecting', logger=None)
        t.start()
        engine.visit(patchset)
        t.stop()

        if engine.bug_accumulator:
            bug_instance_dict[subproject] = engine.bug_accumulator
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
            log_file_name = 'main.csv'
        elif task == TASK_TEST:
            append_file(logfile, '------------------------- Execute Task Test -------------------------\n')
            bug_ins_dict = exec_task(test_paths)
            log_file_name = 'test.csv'
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
    tt = Timer(name='main', logger=None)
    tt.start()
    detect_project('elasticsearch')
    tt.stop()

    for n, time_s in Timer.timers.items():
        print('{}\tElapsed time: {:0.4f} seconds'.format(n, time_s))

"""
                        Time analysis
    ==============================================================
    main	Elapsed time: 226.5561 seconds
    io	Elapsed time: 0.0041 seconds
    parsing	Elapsed time: 4.6717 seconds
    detecting	Elapsed time: 221.6110 seconds
    Itr Detectors	Elapsed time: 219.8802 seconds
    --------------------------------------------------------------
    BitSignedCheck	Elapsed time: 2.5860 seconds
    BitSignedCheckAndBitAndZZDetector	Elapsed time: 2.2407 seconds
    GetResourceDetector	Elapsed time: 4.8040 seconds
    StaticDateFormatDetector	Elapsed time: 1.7554 seconds
    NotThrowDetector	Elapsed time: 1.3979 seconds
*** CollectionAddItselfDetector	Elapsed time: 10.7610 seconds
    FindRoughConstantsDetector	Elapsed time: 1.7028 seconds
    EqualityDetector	Elapsed time: 5.4248 seconds
    CalToNullDetector	Elapsed time: 1.5413 seconds
    SimpleNameDetector1	Elapsed time: 1.6728 seconds
    SimpleNameDetector2	Elapsed time: 2.7698 seconds
    DontCatchIllegalMonitorStateException	Elapsed time: 0.8042 seconds
    ExplicitInvDetector	Elapsed time: 4.0218 seconds
    PublicAccessDetector	Elapsed time: 0.7516 seconds
    DefSerialVersionID	Elapsed time: 6.4999 seconds
*** DefReadResolveMethod	Elapsed time: 14.3363 seconds
*** RemoveAllDetector	Elapsed time: 42.3520 seconds
*** VacuousSelfCallDetector	Elapsed time: 42.4283 seconds
*** NotContainThemselvesDetector	Elapsed time: 42.4808 seconds
    FinalizerOnExitDetector	Elapsed time: 1.5798 seconds
    RandomOnceDetector	Elapsed time: 1.4165 seconds
    RandomD2IDetector	Elapsed time: 1.4786 seconds
    StringCtorDetector	Elapsed time: 1.5100 seconds
    NewLineDetector	Elapsed time: 1.1462 seconds
"""