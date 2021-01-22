import re

import cachetools
from cachetools import cached, LRUCache

from config import CONFIG
from patterns.models.bug_instance import BugInstance
from patterns.models.detectors import Detector
from utils import send, log_message
from patterns.models import priorities

_cache = LRUCache(maxsize=500)


def clear_cache():
    _cache.clear()


def online_search(simple_name: str):
    """
    Search "extends @simple_name" with Github API in the remote repository.
    :param simple_name: Simple name of super class
    :return: The number of search results, or -1 if searching fails
    """
    repo_name = CONFIG.get('repo_name', None)
    if repo_name:
        query = f'https://api.github.com/search/code?q=%22extends+{simple_name}%22+in:file' \
                f'+language:Java+repo:{repo_name}'
        token = CONFIG.get('token', '')
        resp = send(query, token, 3)

        if resp:
            jresp = resp.json()
            if 'total_count' in jresp:
                return jresp['total_count']

        log_message(f'[Online Search Error]{query} No response, or response doesn\'t contain key "total_count"',
                    level='error')

    else:
        log_message(f'[Online Search Error]{query} Attribute "repo_name" not set. '
                    'If you set attribute "enable_online_search" as True, then you should also set "repo_name"',
                    level='error')
    return -1


@cached(cache=_cache, key=lambda simple_name, local_search=None: cachetools.keys.hashkey(simple_name))
def decide_priority(simple_name: str, local_search=None):
    """
    Decide the priority according to search results of local search or online search
    :param simple_name: Simple name of super class
    :param local_search: function passed by Engine to search in current patch set
    :return: MEDIUM_PRIORITY if extended, else IGNORE_PRIORITY
    """

    # local search if enabled
    if CONFIG.get('enable_local_search', False):
        assert local_search is not None
        file_name = local_search(simple_name)
        if file_name:
            return priorities.MEDIUM_PRIORITY
    # online search if enabled
    if CONFIG.get('enable_online_search', False):
        total_count = online_search(simple_name)
        if total_count > 0:
            return priorities.MEDIUM_PRIORITY
        else:
            return None
    # default priority
    return priorities.IGNORE_PRIORITY


class GetResourceDetector(Detector):
    def __init__(self):
        self.pattern = re.compile(r'(?:(\b\w+)\.)?getClass\(\s*\)\.getResource(?:AsStream)?\(')
        Detector.__init__(self)

    def match(self, linecontent: str, filename: str, lineno: int, **kwargs):
        if not all(method in linecontent for method in ['getClass', 'getResource']):
            return

        m = self.pattern.search(linecontent.strip())
        if m:
            obj_name = m.groups()[0]
            if not obj_name or obj_name == 'this':
                simple_name = filename.rstrip('.java').rsplit('/', 1)[-1]  # default class name is the filename
                local_search = kwargs.get('local_search', None)
                priority = decide_priority(simple_name, local_search)

                if priority is None:
                    return

                self.bug_accumulator.append(
                    BugInstance('UI_INHERITANCE_UNSAFE_GETRESOURCE', priority, filename, lineno,
                                'Usage of GetResource may be unsafe if class is extended')
                )
