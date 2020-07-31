import re

from patterns.detectors import Detector
import patterns.utils as utils


class DontCatchIllegalMonitorStateException(Detector):
    '''
    匹配 catch (xxException e1, ..., xxException e2), 并分离出 Exception 类型

    检查到 catch 关键词, 开启多行模式,
    '''

    def __init__(self):
        # 匹配形如 "catch (IOException e)"
        self.regexp = re.compile('catch\s*\((\s*[a-zA-Z0-9\.]+\s+[a-zA-Z0-9\.]+.*?)\)')

    def _visit_patch(self, patch):
        file_name = patch.name

        for hunk in patch:
            idx_add_lines = hunk.addlines
            for i in idx_add_lines:
                content = hunk.lines[i].content[1:]  # 移除开头的 '+'

                if utils.is_comment(content):
                    continue

                match = self.regexp.search(content)
                if match:
                    pass
