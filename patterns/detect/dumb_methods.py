from patterns.detectors import Detector


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
    '''
    def __init__(self):
        self.dm_exit_regex = 'System\.exit\(\d+\)'

    def _visit_patch(self, patch):
        pass