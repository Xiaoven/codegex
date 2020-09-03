import re

from patterns.detectors import Detector
from patterns.bug_instance import BugInstance
import patterns.priorities as Priorities

'''
ref: https://github.com/spotbugs/spotbugs/blob/07bf864b83083c467e29f1b2de58a2cf5aa5c0d6/spotbugs/src/main/java/edu/umd/cs/findbugs/detect/DontUseEnum.java
Only detect "enum" and "assert"
Code containing these pattern are compilable only at java 1.4(enum)/1.3(assert) or lower versions.
'''

reg_word = re.compile('\w+')

class DontUseEnum(Detector):
    def __init__(self):
        self.re_enum = re.compile('enum\s+\w+')
        self.re_assert = re.compile('assert\s+\(*\w')

    def _visit_patch(self, patch):
        for hunk in patch:
            for i in range(len(hunk)):
                # detect all lines in the patch rather than the addition
                if i in hunk.dellines:
                    continue

                line_content = hunk.lines[i].content
                if i in hunk.addlines:
                    line_content = line_content[1:]     # remove "+"

                '''
                step 1: check if line contains keywords
                step 2: check if valid usage
                            example for enum:
                                public enum EType {
                            example for assert:
                                assert object != null;
                                assert (mode >= 0 && mode < 2);
                '''
                words = reg_word.findall(line_content)
                if 'enum' in words:
                    if not self.re_enum.search(line_content):
                        self.bug_accumulator.append(
                            BugInstance('NM_FUTURE_KEYWORD_USED_AS_IDENTIFIER', Priorities.NORMAL_PRIORITY, patch.name,
                                        hunk.lines[i].lineno[1])
                        )
                if 'assert' in words:
                    if not self.re_assert.search(line_content):
                        pass