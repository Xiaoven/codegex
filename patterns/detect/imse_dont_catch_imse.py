import re

from patterns.detectors import Detector
import patterns.utils as utils
from patterns.bug_instance import BugInstance
import patterns.priorities as Priorities


class DontCatchIllegalMonitorStateException(Detector):
    '''
    匹配 catch (xxException e1, ..., xxException e2), 并分离出 Exception 类型
    检查到 catch 关键词, 开启多行模式
    TODO: java.lang.Exception　和　java.lang.Throwable 的检测
    '''

    def __init__(self):
        # 匹配形如 "catch (IOException e)"
        self.regexp = re.compile(r'catch\s*\(\s*([a-zA-Z0-9\.]+\s+[a-zA-Z0-9\.]+.*?)\)')
        self.regexp2 = re.compile(r'([a-zA-Z0-9\.]+)\s+[a-zA-Z0-9\.]+')  # 提取类名

    def _visit_patch(self, patch):
        for hunk in patch:
            idx_add_lines = hunk.addlines
            for i in idx_add_lines:
                content = hunk.lines[i].content[1:]  # 移除开头的 '+'

                if utils.is_comment(content):
                    continue

                match = self.regexp.search(content)
                if match:
                    exp_stat = match.groups()[0]
                    exp_types = self.regexp2.findall(exp_stat)
                    for exp in exp_types:
                        if exp.endswith('IllegalMonitorStateException'):
                            self.bug_accumulator.append(
                                BugInstance('IMSE_DONT_CATCH_IMSE', Priorities.HIGH_PRIORITY,
                                            patch.name, hunk.lines[i].lineno[1],
                                            'Dubious catching of IllegalMonitorStateException')
                            )
