import re
from cachetools import cached, LRUCache

from config import CONFIG
from patterns.models.bug_instance import BugInstance
from patterns.models.detectors import Detector
import patterns.priorities as Priorities
from utils import send, log_message


_cache = LRUCache(maxsize=500)


def clear_cache():
    _cache.clear()


@cached(cache=_cache)
def online_search(simple_name: str):
    """
    Search "extends @simple_name" with Github API in the remote repository.
    :param simple_name: Simple name of super class
    :return: The number of search results, or -1 if searching fails
    """
    if CONFIG.get('enable_online_search', False):
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

            log_message('[Online Search Error] No response, or response doesn\'t contain key "total_count"',
                        level='error')

        else:
            log_message('[Online Search Error] Attribute "repo_name" not set. '
                        'If you set attribute "enable_online_search" as True, then you should also set "repo_name"',
                        level='error')
    return -1

class GetResourceDetector(Detector):
    def __init__(self):
        self.pattern = re.compile(r'(?:(\b\w+)\.)?getClass\(\s*\)\.getResource(?:AsStream)?\(')
        Detector.__init__(self)

    def match(self, linecontent: str, filename: str, lineno: int, get_exact_lineno=None):
        if not all(method in linecontent for method in ['getClass', 'getResource']):
            return

        m = self.pattern.search(linecontent.strip())
        if m:
            obj_name = m.groups()[0]
            if not obj_name or obj_name == 'this':
                priority = Priorities.LOW_PRIORITY

                simple_name = filename.rstrip('.java').rsplit('/', 1)[-1]  # default class name is the filename
                total_count = online_search(simple_name)

                if total_count == 0:
                    return
                elif total_count > 0:
                    priority = Priorities.MEDIUM_PRIORITY
                else:  # total_count == -1  Cannot decide
                    priority = Priorities.IGNORE_PRIORITY

                self.bug_accumulator.append(
                    BugInstance('UI_INHERITANCE_UNSAFE_GETRESOURCE', priority, filename, lineno,
                                'Usage of GetResource may be unsafe if class is extended')
                )


