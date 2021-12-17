import regex

from patterns.models.priorities import *
from patterns.models.bug_instance import BugInstance
from patterns.models.detectors import Detector, get_exact_lineno
import os

class UnnecessaryMathDetector(Detector):
    def __init__(self):
        self.pattern = regex.compile(r'')
        self.zeroMethods = ("acos",
                            "asin",
                            "atan",
                            "atan2",
                            "cbrt",
                            "cos",
                            "cosh",
                            "exp",
                            "expm1",
                            "log",
                            "log10",
                            "pow",
                            "sin",
                            "sinh",
                            "sqrt",
                            "tan",
                            "tanh",
                            "toDegrees",
                            "toRadians",
                            )

        self.oneMethods = ("acos",
                           "asin",
                           "atan",
                           "cbrt",
                           "exp",
                           "log",
                           "log10",
                           "pow",
                           "sqrt",
                           "toDegrees",
                           )
        self.anyMethods = ("abs",
                           "ceil",
                           "floor",
                           "rint",
                           "round",)
        self.pattern = regex.compile(r'')
        Detector.__init__(self)

    def match(self, context):
        # TODO: Don't complain about unnecessary math calls in class initializers,
        #  since they may be there to improve readability.
        pass
