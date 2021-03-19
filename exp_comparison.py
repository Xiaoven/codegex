import os
from os import path
from subprocess import check_output
import re
import json
import shutil
from patterns.models.context import Context
from patterns.models.engine import DefaultEngine
from rparser import parse
from timer import Timer

BASE_PATH = '/home/zhouying/git/rbugs'
EXEC_LOG_PATH = '/home/zhouying/Documents/workspace/rbugs/experiment/log/exepath'
REPORT_PATH = '/home/zhouying/Documents/workspace/rbugs/experiment/log/report/rbugs'
REPO_PATH = '/home/zhouying/Documents/workspace/rbugs/experiment/top100repos'
EXECUTE_PATH = BASE_PATH + '/execute_log'
if os.path.exists(REPORT_PATH):
    shutil.rmtree(REPORT_PATH)
if os.path.exists(EXECUTE_PATH):
    shutil.rmtree(EXECUTE_PATH)
os.makedirs(REPORT_PATH, exist_ok=True)
os.makedirs(EXECUTE_PATH, exist_ok=True)

TASK_MAIN = 'task_main'
TASK_TEST = 'task_test'

JAVA_FILE_PATTERN = re.compile(r'^(.+?)/src/(main|test)/java/')
ANALYZE_FILE = re.compile(r'\[java\] \w+\s+\d+: Analyzing classes \(')


def append_file(file_path: str, content: str):
    with open(file_path, 'a') as f:
        f.write(content)


def write_file(file_path: str, content: str):
    with open(file_path, 'w') as f:
        f.write(content)


def exec_task(file_list):
    bug_instances = list()
    context = Context()
    engine = DefaultEngine(context)

    # generate patch set
    patchset = []
    for file_path in file_list:
        with open(file_path, 'r') as f:
            patch = parse(f.read(), is_patch=False, name=file_path)
            patchset.append(patch)

    # run detectors
    if patchset:
        engine.visit(*patchset)
        bug_instances = engine.filter_bugs(level='low')

    return bug_instances


def gen_analyze_paths():
    ls_result = os.listdir(EXEC_LOG_PATH)
    project_names = [name[:-4] for name in ls_result if name.endswith('.log')]
    for name in project_names:
        files_to_analyze = set()
        with open(path.join(EXEC_LOG_PATH, name + '.log'), 'r') as f:
            for line in f:
                line = line.strip()
                if ANALYZE_FILE.match(line):
                    tmp = line.split()
                    if tmp:
                        output = check_output(['find', path.join(REPO_PATH, name), '-path', f'*{tmp[-1]}.java']).decode('utf-8')
                        if output.strip():
                            for p in output.splitlines():
                                if '/src/main/java/' in p or '/src/test/java/' in p:
                                    files_to_analyze.add(p.strip())
        if files_to_analyze:
            with open(path.join(EXECUTE_PATH, name + '.json'), 'w') as out:
                json.dump(list(files_to_analyze), out)


def detect_project(project_name: str):
    # load files to analyze
    try:
        with open(path.join(EXECUTE_PATH, project_name + '.json'), 'r') as f:
            path_list = json.load(f)

        if path_list:
            # analyze files
            bug_instances = exec_task(path_list)

            # write reports
            if bug_instances:
                repo_report_path = path.join(REPORT_PATH, project_name)
                os.makedirs(repo_report_path, exist_ok=True)
                # write csv
                content = str()
                for ins in bug_instances:
                    content += f'{ins.type},{ins.file_name},{ins.line_no}\n'

                write_file(f'{repo_report_path}/{project_name}.csv', content)
                # write bug instance json
                with open(f'{repo_report_path}/bug_instances.json', 'w') as out:
                    bugs_json = dict()
                    bugs_json['repo'] = project_name
                    bugs_json['total'] = len(bug_instances)
                    bugs_json['items'] = [bug.__dict__ for bug in bug_instances]
                    json.dump(bugs_json, out)
    except FileNotFoundError as fnf_error:
        print(fnf_error)
        


if __name__ == '__main__':
    # Step 1: get files to analyze by spotbugs' execution log
    gen_analyze_paths()

    # Step 2: run rbugs against the files in Step 1
    total_timer = Timer(name='Total', logger=None)
    total_timer.start()

    project_name_list = os.listdir(REPO_PATH)
    for project_name in project_name_list:
        project_timer = Timer(name=project_name, logger=None)
        project_timer.start()

        detect_project(project_name)

        project_timer.stop()

    total_timer.stop()

    # Step 3: write time dict to file
    time_log = path.join(REPORT_PATH, 'time.log')
    with open(time_log, 'w') as f:
        f.write('\n'.rjust(41, '=') + f'Total Time: {Timer.timers["Total"]}\n' + '\n'.rjust(41, '=') + '\n')
        for project_name in project_name_list:
            f.write('{:<30s} {:<10f} seconds\n'.format(project_name, Timer.timers[project_name]))
        f.write(format('', '->40s') + '\n')
        for key, time_s in Timer.timers.items():
            if key != 'Total' and key not in project_name_list:
                f.write('{:<30s} {:<10f} seconds\n'.format(key, time_s))
