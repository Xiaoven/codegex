import glob
import json
import re
from os import path
import json

from patterns.models.engine import DefaultEngine
from rparser import parse
from utils import logger, logger_add, TRACE
from config import CONFIG
from timer import Timer


root = 'PullRequests'
report_path = 'PullRequests/report'


def find_missing_pr():
    paths = glob.glob('PullRequests/java/links/**/*.csv', recursive=True)

    total_link_cnt = 0
    missing_file_cnt = 0
    link_dic = dict()

    for p in paths:
        with open(p, 'r') as f:
            for line in f:
                link = line.strip().split(',')[0]
                if link:
                    total_link_cnt += 1

                    if link in link_dic:
                        link_dic[link] += 1
                        # print('[Duplicate]: ', line)
                    else:
                        link_dic[link] = 0

                    file_path = link.replace('https://api.github.com/repos/',
                                             'PullRequests/java/files/') + '.json'

                    if not path.exists(file_path):
                        missing_file_cnt += 1
                        print('[Missing]: ', line)

    print('==========================')
    print(f'missing_file_cnt = {missing_file_cnt}')
    print(f'total_link_cnt = {total_link_cnt}')
    print(f'unique link = {len(link_dic)}')


def report_diversity():
    paths = glob.glob(f'{report_path}/*.log', recursive=True)
    re_pattern_name = re.compile(r'Confidence:([A-Z_0-9]+)$')
    diversity = dict()

    for p in paths:
        with open(p, 'r') as file_to_read:
            for line in file_to_read:
                m = re_pattern_name.search(line)
                if m:
                    pattern_name = m.groups()[0]
                    if pattern_name in diversity:
                        diversity[pattern_name] += 1
                    else:
                        diversity[pattern_name] = 1

    with open(f'{report_path}/diversity.json', 'w') as outfile:
        json.dump(diversity, outfile)


def sum_time_and_warnings():
    with open('/Users/audrey/Documents/GitHub/rbugs/PullRequests/report/diversity.json', 'r') as f:
        jfile = json.load(f)
        sum = 0
        for k, v in jfile.items():
            if k not in ("SA_SELF_COMPARISON", "VA_FORMAT_STRING_USES_NEWLINE","SA_SELF_COMPUTATION"):
                sum += v
        print(f'sum of diversity = {sum}')

    with open('/Users/audrey/Documents/GitHub/rbugs/PullRequests/report/timer.json', 'r') as f:
        jfile = json.load(f)
        sum = 0
        for k, v in jfile.items():
            sum += v
        print(f'sum of time = {sum}')


def get_modified_patchset(path):
    patchset = []
    with open(path, 'r') as jf:
        jfile = json.load(jf)
        for file in jfile:
            name = file['filename']

            if name.endswith('.java'):
                if 'patch' in file and file['status'] != 'removed':
                    patch = parse(file['patch'], name=name)
                    patch.type = file['status']

                    patchset.append(patch)
    return patchset


def run():
    paths = glob.glob(f'{root}/**/*.json', recursive=True)

    # logger name
    logger.remove(TRACE)
    cnt = 1
    trace = logger_add(report_path, f'{cnt}.log')
    has_bug = False

    engine = DefaultEngine()
    CONFIG['enable_local_search'] = True
    CONFIG['enable_online_search'] = True
    CONFIG['token'] = ''

    re_repo = re.compile(r'PullRequests/java/files/(.+?)/pulls/(\d+)')

    for p in paths:
        m = re_repo.search(p)
        if m:
            repo_name = CONFIG['repo_name'] = m.groups()[0]
            pr_id = m.groups()[1]
        else:
            continue

        if has_bug:
            logger.remove(trace)
            cnt += 1
            trace = logger_add(report_path, f'{cnt}.log')
            has_bug = False

        patchset = get_modified_patchset(p)
        if patchset:
            pr_timer = Timer(repo_name + '-' + pr_id, logger=None)
            pr_timer.start()
            engine.visit(*patchset)
            if engine.bug_accumulator:
                engine.report(level='low')
                has_bug = True
            pr_timer.stop()

        if has_bug:
            logger.info(p)

    with open(path.join(report_path, 'timer.json'), 'w') as logfile:
        json.dump(Timer.timers, logfile)


if __name__ == '__main__':
    run()
