import glob
import re
from os import path
import json

from patterns.models.context import Context
from patterns.models.engine import DefaultEngine
from rparser import parse
from utils import create_missing_dirs
from timer import Timer


root = 'PullRequests'
report_path = 'PullRequests/report'

RE_SHA = re.compile(r'https://github\.com/[^/]+/[^/]+/blob/(\w+)/')


def _get_sha(blob_url: str):
    try:
        m = RE_SHA.search(blob_url)
        if m:
            return m.groups()[0]

    except TypeError as e:
        # "blob_url": null
        return ''


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


# def report_diversity():
#     paths = glob.glob(f'{report_path}/*.log', recursive=True)
#     re_pattern_name = re.compile(r'Confidence:([A-Z_0-9]+)$')
#     diversity = dict()
#
#     for p in paths:
#         with open(p, 'r') as file_to_read:
#             for line in file_to_read:
#                 m = re_pattern_name.search(line)
#                 if m:
#                     pattern_name = m.groups()[0]
#                     if pattern_name in diversity:
#                         diversity[pattern_name] += 1
#                     else:
#                         diversity[pattern_name] = 1
#
#     with open(f'{report_path}/diversity.json', 'w') as outfile:
#         json.dump(diversity, outfile)


def sum_time_and_warnings():
    with open('/PullRequests/report_bk/diversity.json', 'r') as f:
        jfile = json.load(f)
        sum = 0
        for k, v in jfile.items():
            if k not in ("SA_SELF_COMPARISON", "VA_FORMAT_STRING_USES_NEWLINE", "SA_SELF_COMPUTATION"):
                sum += v
        print(f'sum of diversity = {sum}')

    with open('/PullRequests/report_bk/timer.json', 'r') as f:
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
                    if 'blob_url' in file:
                        patch.sha = _get_sha(file['blob_url'])
                    patchset.append(patch)
    return patchset


def run():
    paths = glob.glob(f'{root}/**/*.json', recursive=True)

    context = Context()
    context.enable_online_search()
    engine = DefaultEngine(context)

    re_repo = re.compile(r'PullRequests/java/files/(.+?)/pulls/(\d+)')

    for p in paths:
        m = re_repo.search(p)
        if m:
            repo_name = m.groups()[0]
            pr_id = m.groups()[1]
            engine.context.update_repo_name(repo_name)
        else:
            continue

        patchset = get_modified_patchset(p)
        if patchset:
            pr_timer = Timer(repo_name + '-' + pr_id, logger=None)
            pr_timer.start()
            engine.visit(*patchset)

            bugs = engine.filter_bugs(level='low')
            if bugs:
                save_path = f'{report_path}/{repo_name}/{pr_id}'
                create_missing_dirs(save_path)
                with open(f'{save_path}/report.json', 'w') as out:
                    bugs_json = dict()
                    bugs_json['repo'] = repo_name
                    bugs_json['id'] = pr_id
                    bugs_json['total'] = len(bugs)
                    bugs_json['items'] = [bug.__dict__ for bug in bugs]
                    json.dump(bugs_json, out)
            pr_timer.stop()

    with open(path.join(report_path, 'timer.json'), 'w') as logfile:
        json.dump(Timer.timers, logfile)


if __name__ == '__main__':
    run()
