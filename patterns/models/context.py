class Context:
    """
    A context object contains state configurations and objects (patch set, patch, hunk and line) currently to be checked.
    It offers information for detectors.
    """

    def __init__(self):
        # current objects
        self.patch_set = None
        self.cur_patch = None
        self.cur_hunk = None
        self.cur_line = None
        self.cur_line_idx = -1

        # configuration
        self._online_search, self._repo_name, self._token = False, None, None
        self._local_search = True

    def set_patch_set(self, patch_set: tuple):
        self.patch_set = patch_set
        self.cur_patch = None
        self.cur_hunk = None
        self.cur_line = None
        self.cur_line_idx = -1

    def online_search(self):
        return self._online_search

    def enable_online_search(self, github_repo_name: str, github_token=''):
        if github_repo_name:
            self._online_search = True
            self._repo_name = github_repo_name
            if github_token:
                self._token = github_token

    def disable_online_search(self):
        self._online_search = False
        self._repo_name = None
        self._token = None

    def get_online_search_info(self):
        return self._repo_name, self._token

    def local_search(self):
        return self._local_search

    def enable_local_search(self):
        self._local_search = True

    def disable_local_search(self):
        self._local_search = False
