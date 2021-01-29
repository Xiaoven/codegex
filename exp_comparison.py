import os
from os import path
from subprocess import check_output
import re

from patterns.models.context import Context
from patterns.models.engine import DefaultEngine
from rparser import parse
from timer import Timer

BASE_PATH = '/home/xiaowen/Project/rbugs_experiments/github-repos'
LOG_PATH = 'comparison_exp'

TASK_MAIN = 'task_main'
TASK_TEST = 'task_test'

JAVA_FILE_PATTERN = re.compile(r'^(.+?)/src/(main|test)/java/')


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
    context = Context()
    engine = DefaultEngine(context)

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

        engine.visit(*patchset)

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
                    content += f'{ins.type},{ins.file_name},{ins.line_no}\n'
                write_file(report_path, content)
                append_file(logfile, f'Found {len(bug_instances)} violations: f{report_path}\n')

    if unknown_tasks:
        append_file(logfile, '------------------------- Unknown Tasks -------------------------\n'
                    + '\n'.join(unknown_tasks) + '\n')


if __name__ == '__main__':
    total_timer = Timer(name='Total', logger=None)
    total_timer.start()

    project_name_list = os.listdir(BASE_PATH)
    for project_name in project_name_list:
        project_timer = Timer(name=project_name, logger=None)
        project_timer.start()

        detect_project(project_name)

        project_timer.stop()

    total_timer.stop()

    time_log = path.join(LOG_PATH, 'time.log')
    with open(time_log, 'w') as f:
        f.write('\n'.rjust(41, '=') + f'Total Time: {Timer.timers["Total"]}\n' + '\n'.rjust(41, '=') + '\n')
        for project_name in project_name_list:
            f.write('{:<30s} {:<10f} seconds\n'.format(project_name, Timer.timers[project_name]))
        f.write(format('', '->40s') + '\n')
        for key, time_s in Timer.timers.items():
            if key != 'total' or key not in project_name_list:
                f.write('{:<30s} {:<10f} seconds\n'.format(key, time_s))
