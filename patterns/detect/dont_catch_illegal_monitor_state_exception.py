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

    def match(self, linecontent: str, filename: str, lineno: int, **kwargs):
        match = self.p_catch.search(linecontent.strip())

        if match:
            params = match.groups()[0]
            defs = params.split(',')
            for d in defs:
                exception_class = d.split()[0]

                get_exact_lineno = kwargs.get('get_exact_lineno', None)
                if get_exact_lineno:
                    tmp = get_exact_lineno(exception_class)
                    if tmp:
                        lineno = tmp[1]

                if exception_class.endswith('IllegalMonitorStateException'):
                    self.bug_accumulator.append(
                        BugInstance('IMSE_DONT_CATCH_IMSE', priorities.HIGH_PRIORITY,
                                    filename, lineno,
                                    'Dubious catching of IllegalMonitorStateException')
                    )
                    break
