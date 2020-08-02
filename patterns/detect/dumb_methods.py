from patterns.detectors import Detector
import patterns.utils as utils


class DmExit(Detector):
    '''
    TODO: 对所在的 method 做一些限制
    if (!isPublicStaticVoidMain && seen == Const.INVOKESTATIC && "java/lang/System".equals(getClassConstantOperand())
                        && "exit".equals(getNameConstantOperand()) && !"processWindowEvent".equals(getMethodName())
                        && !getMethodName().startsWith("windowClos") && getMethodName().indexOf("exit") == -1
                        && getMethodName().indexOf("Exit") == -1 && getMethodName().indexOf("crash") == -1
                        && getMethodName().indexOf("Crash") == -1 && getMethodName().indexOf("die") == -1
                        && getMethodName().indexOf("Die") == -1 && getMethodName().indexOf("main") == -1) {
                    accumulator.accumulateBug(new BugInstance(this, "DM_EXIT", getMethod().isStatic() ? LOW_PRIORITY
                            : NORMAL_PRIORITY).addClassAndMethod(this), SourceLineAnnotation.fromVisitedInstruction(this));

    识别方法声明的正则：
        (?:(?:public|private|protected|static|final|native|synchronized|abstract|transient)\s+)+[$_\w<>\[\]\.]*\s+[$_\w]+\s*\(
    '''
    def __init__(self):
        self.regex_method = '(?:(?:public|private|protected|static|final|native|synchronized|abstract|transient)\s+)+[$_\w<>\[\]\.]*\s+[$_\w]+\s*\('
        self.regex_exit = 'System\.exit\(\d+\)'

    def _visit_patch(self, patch):
        file_name = patch.name

        for hunk in patch:
            idx_add_lines = hunk.addlines

            # 寻找 system.exit 所在行数
            idx_exit = []
            for i in idx_add_lines:
                content = hunk.lines[i].content[1:]
                if utils.is_comment(content):
                    continue

                match = self.regex_exit.search(content)
                if match:
                    idx_exit.append(i)

            # 往回寻找 method definition
            for i in idx_exit:
                cur = i-1
                while cur >= 0:

                    cur -= 1
                
