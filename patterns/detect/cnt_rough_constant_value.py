from patterns.utils import logger, is_comment
import patterns.priorities as Priorities
from patterns.detectors import Detector
from patterns.bug_instance import BugInstance
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
    BadConstant(math.pi, 1, "Math.PI", Priorities.HIGH_PRIORITY),
    BadConstant(math.pi, 1 / 2.0, "Math.PI/2", Priorities.NORMAL_PRIORITY),
    BadConstant(math.pi, 1 / 3.0, "Math.PI/3", Priorities.LOW_PRIORITY),
    BadConstant(math.pi, 1 / 4.0, "Math.PI/4", Priorities.LOW_PRIORITY),
    BadConstant(math.pi, 2, "2*Math.PI", Priorities.NORMAL_PRIORITY),
    BadConstant(math.e, 1, "Math.E", Priorities.LOW_PRIORITY)
]


def get_priority(bad_constant: BadConstant, const_val):
    diff = bad_constant.diff(const_val)

    if diff > 1e-3:
        return Priorities.IGNORE_PRIORITY  # 差值太大，不太可能是近似值
    elif diff > 1e-4:
        return bad_constant.base_priority + 1
    elif diff < 1e-6:
        p = bad_constant.base_priority - 1
        return p if p > 0 else 1
    else:
        return bad_constant.base_priority


def check_const(const_val: float):
    best_p, best_const = Priorities.IGNORE_PRIORITY, None
    for bad_const in BAD_CONSTANTS:
        priority = get_priority(bad_const, const_val)
        if priority < best_p:
            best_p = priority
            best_const = bad_const
    return best_p, best_const


class FindRoughConstants(Detector):
    def __init__(self):
        self.regexp = re.compile('(\d*\.\d+)')

    def _visit_patch(self, patch):
        file_name = patch.name

        for hunk in patch:
            idx_add_lines = hunk.addlines
            for i in idx_add_lines:
                content = hunk.lines[i].content[1:]  # 移除开头的 '+'

                if is_comment(content):
                    continue

                match = self.regexp.findall(content)

                for m in match:
                    float_const = float(m)
                    p, bad_const = check_const(float_const)
                    if p < Priorities.IGNORE_PRIORITY:
                        bug_ins = RoughConstantValueBugInstance("CNT_ROUGH_CONSTANT_VALUE", p, file_name, hunk.lines[i].lineno[1])
                        bug_ins.gen_description(float_const, bad_const)
                        self.bug_accumulator.append(bug_ins)

    def report(self):
        for bug_ins in self.bug_accumulator:
            logger.warning(str(bug_ins))


class RoughConstantValueBugInstance(BugInstance):
    def gen_description(self, constant: float, bad_constant: BadConstant):
        self.constant = constant
        self.bad_constant = bad_constant
        self.description = 'Rough value of %s found: %s' % (bad_constant.replacement, str(constant))
