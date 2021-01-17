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
    root = 'PullRequests'
    report_path = 'PullRequests/report'
    paths = glob.glob(f'{root}/**/*.json', recursive=True)

    # logger name
    logger.remove(TRACE)
    cnt = 1
    trace = logger_add(report_path, f'{cnt}.log')
    has_bug = False

    engine = DefaultEngine()
    CONFIG['enable_local_search'] = True
    CONFIG['enable_online_search'] = True
    CONFIG['token'] = 'e168ea8300580a7d0159a2fb5225c08f1cb0c235'

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
                engine.report(level='ignore')
                has_bug = True
            pr_timer.stop()

        if has_bug:
            logger.info(p)

    with open(path.join(report_path, 'timer.json'), 'w') as logfile:
        json.dump(Timer.timers, logfile)
