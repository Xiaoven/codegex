import re

from config import CONFIG
from patterns.bug_instance import BugInstance
from patterns.detectors import Detector
import patterns.priorities as Priorities
from patterns.utils import send


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

                if CONFIG.get('enable_online_search', False):
                    repo_name = CONFIG.get('repo_name', None)
                    if repo_name:
                        simple_name = filename.rstrip('.java').rsplit('/', 1)[-1]  # default class name is the filename
                        query = f'https://api.github.com/search/code?q=%22extends+{simple_name}%22+in:file' \
                                f'+language:Java+repo:{repo_name}'
                        token = CONFIG.get('token', '')
                        resp = send(query, token, 3)
                        if resp:
                            jresp = resp.json()
                            if 'total_count' in jresp and jresp['total_count'] > 0:
                                priority = Priorities.MEDIUM_PRIORITY
                            else:
                                return
                        else:
                            return
                self.bug_accumulator.append(
                    BugInstance('UI_INHERITANCE_UNSAFE_GETRESOURCE', priority, filename, lineno,
                                'Usage of GetResource may be unsafe if class is extended')
                )
