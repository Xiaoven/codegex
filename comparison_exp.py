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
from patterns.detect.find_unrelated_types_in_generic_container import SuspiciousCollectionMethodDetector
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
# DETECTORS = [BitSignedCheck(), BitSignedCheckAndBitAndZZDetector(), GetResourceDetector(), StaticDateFormatDetector(),
#              NotThrowDetector(), CollectionAddItselfDetector(), FindRoughConstantsDetector(), EqualityDetector(),
#              CalToNullDetector(), SimpleNameDetector1(), SimpleNameDetector2(), DontCatchIllegalMonitorStateException(),
#              ExplicitInvDetector(), PublicAccessDetector(), DefSerialVersionID(), DefReadResolveMethod(),
#              SuspiciousCollectionMethodDetector(), FinalizerOnExitDetector(),
#              RandomOnceDetector(), RandomD2IDetector(), StringCtorDetector(), NewLineDetector()
#              ]

DETECTORS = [SuspiciousCollectionMethodDetector(), SimpleNameDetector1()]


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
    engine = DefaultEngine(DETECTORS)

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

    cnt_source, cnt_test = 0, 0

    for file_path in output.splitlines():
        m = JAVA_FILE_PATTERN.match(file_path)
        if m:
            g = m.groups()

            if g[1] == 'main' in file_path:
                tmp_paths = source_paths.get(g[0], list())
                tmp_paths.append(file_path)
                source_paths[g[0]] = tmp_paths
                cnt_source += 1
            elif g[1] == 'test' in file_path:
                tmp_paths = source_paths.get(g[0], list())
                tmp_paths.append(file_path)
                test_paths[g[0]] = tmp_paths
                cnt_test += 1
            else:
                other_paths.append(file_path)

            # if cnt_source + cnt_test >= 100:
            #     break

    log_dir = path.join(LOG_PATH, project_name)
    os.makedirs(log_dir, exist_ok=True)
    logfile = path.join(log_dir, 'detect.log')
    empty_file(logfile)

    append_file(logfile, f'source file num: {cnt_source}\ntest file num: {cnt_test}\n')

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
    for project_name in ['elasticsearch']:
        tt = Timer(name=project_name, logger=None)
        tt.start()
        detect_project(project_name)
        tt.stop()

    for n, time_s in Timer.timers.items():
        print('{}\tElapsed time: {:0.4f} seconds'.format(n, time_s))


"""
TODO: count java files for each project

    =============================== Time for Each Project ===============================    
    rocketmq	                Elapsed time: 9.8217 seconds     --> 31.389 s       731 + 246         
    RxJava	                    Elapsed time: 8.7811 seconds     --> 23s            845 + 960
    fastjson	                Elapsed time: 4.0155 seconds     --> 6.439 s        190 + 2784
    BungeeCord	                Elapsed time: 1.9693 seconds     --> 28.522 s       253 + 18 files
    animated-gif-lib-for-java	Elapsed time: 0.0927 seconds     --> 2.507 s        4 + 2 files
    elasticsearch	            Elapsed time: 135.1377 seconds   --> 1m 39s         9012 + 4712
    HikariCP	                Elapsed time: 0.5329 seconds     --> 4.556 s        43 + 55
    FizzBuzzEnterpriseEdition	Elapsed time: 0.4199 seconds     --> 4s             87+2
    nanohttpd	                Elapsed time: 0.5527 seconds     --> 21s            47 + 40
    CS416	                    Elapsed time: 0.1705 seconds     --> 2.836 s        29+0
    =============================== Other Time =============================== 
    io	            Elapsed time: 0.0091 seconds
    parsing	        Elapsed time: 5.9415 seconds
    detecting	    Elapsed time: 155.1335 seconds
    Itr Detectors	Elapsed time: 153.3072 seconds
    =============================== Time for Each Detector ===============================
    BitSignedCheck	                    Elapsed time: 2.8541 seconds        \(\s*((?:(?P<aux1>\((?:[^()]++|(?&aux1))*\))|[\w.])++)\s*&\s*((?:(?&aux1)|[\w.])+)\s*\)\s*>\s*0
    BitSignedCheckAndBitAndZZDetector	Elapsed time: 2.5732 seconds        \(\s*((?:(?P<aux1>\((?:[^()]++|(?&aux1))*\))|[\w.])++)\s*&\s*0\s*\)\s*==\s*0
    GetResourceDetector	                Elapsed time: 5.5114 seconds
    StaticDateFormatDetector	        Elapsed time: 1.9757 seconds
    NotThrowDetector	                Elapsed time: 1.6360 seconds
    CollectionAddItselfDetector	        Elapsed time: 12.5186 seconds
    FindRoughConstantsDetector	        Elapsed time: 1.9394 seconds
    EqualityDetector	                Elapsed time: 6.2776 seconds
    CalToNullDetector	                Elapsed time: 1.7546 seconds
    SimpleNameDetector1	                Elapsed time: 1.9138 seconds        class\s+((?P<name>[\w\.\s<>,])+)\s+extends\s+((?:(?!implements)(?&name))+)
    SimpleNameDetector2	                Elapsed time: 3.3018 seconds        class\s+((?:(?!extends)(?P<name>[\w\.\s<>,]))+)\s+(?&name)*implements\s+((?&name)+)
                                                                            interface\s+((?P<name>[\w\.\s<>,])+)\s+extends\s+((?&name)+)
    DontCatchIllegalMonitorStateException	Elapsed time: 0.9246 seconds
    ExplicitInvDetector	                Elapsed time: 4.7506 seconds
    PublicAccessDetector	            Elapsed time: 0.8796 seconds
    DefSerialVersionID	                Elapsed time: 7.1743 seconds
    DefReadResolveMethod	            Elapsed time: 15.4059 seconds
*** SuspiciousCollectionMethodDetector	Elapsed time: 50.6662 seconds
FinalizerOnExitDetector	                Elapsed time: 1.7634 seconds
    RandomOnceDetector	                Elapsed time: 1.6661 seconds        new\s+[\w\.]*Random(?:(?P<aux1>\((?:[^()]++|(?&aux1))*\)))++\.next\w*\(\s*\)
    RandomD2IDetector	                Elapsed time: 1.6886 seconds
    StringCtorDetector	                Elapsed time: 1.6286 seconds        new\s+String\s*(?P<aux1>\(((?:[^()]++|(?&aux1))*)\))
    NewLineDetector	                    Elapsed time: 1.2494 seconds        
"""