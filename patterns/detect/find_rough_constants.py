
from models.detectors import *
from models.bug_instance import Confidence, BugInstance
from utils.utils import get_string_ranges, in_range
import re

import math


class BadConstant:
    def __init__(self, base, factor, replacement, base_priority):
        self.base = base
        self.factor = factor
        self.value = self.base * self.factor
        self.replacement = replacement  # 字符串描述
        self.base_priority = base_priority

    def diff(self, candidate: float):
        return abs(candidate - self.value) / self.value


BAD_CONSTANTS = [
    BadConstant(math.pi, 1, "Math.PI", Confidence.HIGH),
    BadConstant(math.pi, 1 / 2.0, "Math.PI/2", Confidence.MEDIUM),
    BadConstant(math.pi, 1 / 3.0, "Math.PI/3", Confidence.LOW),
    BadConstant(math.pi, 1 / 4.0, "Math.PI/4", Confidence.LOW),
    BadConstant(math.pi, 2, "2*Math.PI", Confidence.MEDIUM),
    BadConstant(math.e, 1, "Math.E", Confidence.LOW)
]


def get_priority(bad_constant: BadConstant, const_val):
    diff = bad_constant.diff(const_val)

    if diff > 1e-3:
        return Confidence.IGNORE  # 差值太大，不太可能是近似值
    elif diff > 1e-4:
        return Confidence(bad_constant.base_priority.value + 1)
    elif diff < 1e-6:
        confidenceValue = bad_constant.base_priority.value - 1
        return Confidence(confidenceValue) if confidenceValue > 0 else bad_constant.base_priority
    else:
        return bad_constant.base_priority


def check_const(const_val: float):
    best_p, best_const = Confidence.IGNORE, None
    for bad_const in BAD_CONSTANTS:
        priority = get_priority(bad_const, const_val)
        if priority.value < best_p.value:
            best_p = priority
            best_const = bad_const
    return best_p, best_const


class FindRoughConstantsDetector(Detector):
    def __init__(self):
        self.regexp = re.compile(r'(\d*\.\d+)')
        Detector.__init__(self)

    def match(self, context):
        line_content = context.cur_line.content
        its = self.regexp.finditer(line_content)
        string_ranges = get_string_ranges(line_content)
        for m in its:
            if in_range(m.start(0), string_ranges):
                continue
            float_const = float(m.group(0))
            p, bad_const = check_const(float_const)
            if p.value < Confidence.IGNORE.value:
                line_no = get_exact_lineno(m.end(0), context.cur_line)[1]
                bug_ins = RoughConstantValueBugInstance("CNT_ROUGH_CONSTANT_VALUE", p, context.cur_patch.name, line_no,
                                                        sha=context.cur_patch.sha, line_content=context.cur_line.content)
                bug_ins.gen_description(float_const, bad_const)
                self.bug_accumulator.append(bug_ins)
                return


class RoughConstantValueBugInstance(BugInstance):
    def gen_description(self, constant: float, bad_constant: BadConstant):
        self.constant = constant
        self.replacement = bad_constant.replacement
        self.description = 'Rough value of %s found: %s' % (self.replacement, str(constant))
