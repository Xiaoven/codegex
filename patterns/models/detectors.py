from patterns.models.context import Context
from utils import send


def online_search(query: str, token='', search_parent=False, repo_name=''):
    resp = send(query, token, 3)
    if resp:
        resp = resp.json()
        if 'total_count' in resp:
            if resp['total_count'] == 0 and search_parent and repo_name:
                # get parent repo name
                resp = send(f'https://api.github.com/repos/{repo_name}')
                if resp:
                    resp = resp.json()
                    # forked repositories are not currently searchable
                    if 'fork' in resp and resp['fork']:
                        parent_full_name = ''
                        if 'parent' in resp and 'full_name' in resp['parent']:
                            parent_full_name = resp['parent']['full_name']
                        elif 'source' in resp and 'full_name' in resp['source']:
                            parent_full_name = resp['source']['full_name']
                        # search in parent
                        if parent_full_name:
                            new_query = query.replace(repo_name, parent_full_name)
                            return online_search(new_query, token)
            else:
                return resp
    return None



class Detector:
    def __init__(self):
        self.bug_accumulator = []

    def match(self, context: Context):
        """
        Match single line and generate bug instance using regex pattern
        :param context: context object
        :return: None
        """
        pass

    def reset_bug_accumulator(self):
        self.bug_accumulator = list()
