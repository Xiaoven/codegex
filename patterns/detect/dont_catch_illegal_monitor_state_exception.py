import re

from patterns.detectors import Detector
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
        self.p_catch = re.compile(r'catch\s*\(([^()]+)\)')
        Detector.__init__(self)

    def match(self, linecontent: str, filename: str, lineno: int, get_exact_lineno=None):
        match = self.p_catch.search(linecontent)
        if lineno == 4:
            print(lineno)
        if match:
            params = match.groups()[0]
            defs = params.split(',')
            for d in defs:
                exception_class = d.split()[0]

                if get_exact_lineno:
                    lineno = get_exact_lineno(exception_class)[0]

                if exception_class.endswith('IllegalMonitorStateException'):
                    self.bug_accumulator.append(
                        BugInstance('IMSE_DONT_CATCH_IMSE', Priorities.HIGH_PRIORITY,
                                    filename, lineno,
                                    'Dubious catching of IllegalMonitorStateException')
                    )
                    break
