import re

from patterns.models.detectors import Detector
from patterns.models.bug_instance import BugInstance
from patterns.models import priorities


class DontCatchIllegalMonitorStateException(Detector):
    '''
    匹配 catch (xxException e1, ..., xxException e2), 并分离出 Exception 类型
    检查到 catch 关键词, 开启多行模式
    TODO: java.lang.Exception　和　java.lang.Throwable 的检测
    '''

    def __init__(self):
        # 匹配形如 "catch (IOException e)"
        self.p_catch = re.compile(r'catch\s*\(([^()]+)\)')
        Detector.__init__(self)

    def match(self, context):
        line_content = context.cur_line.content
        line_no = context.cur_line.lineno[1]
        match = self.p_catch.search(line_content.strip())

        if match:
            params = match.groups()[0]
            defs = params.split(',')
            for d in defs:
                exception_class = d.split()[0]

                if hasattr(context.cur_line, 'get_exact_lineno'):
                    tmp = context.cur_line.get_exact_lineno(exception_class)
                    if tmp:
                        line_no = tmp[1]

                if exception_class.endswith('IllegalMonitorStateException'):
                    self.bug_accumulator.append(
                        BugInstance('IMSE_DONT_CATCH_IMSE', priorities.HIGH_PRIORITY,
                                    context.cur_patch.name, line_no,
                                    'Dubious catching of IllegalMonitorStateException', sha=context.cur_patch.sha)
                    )
                    return
