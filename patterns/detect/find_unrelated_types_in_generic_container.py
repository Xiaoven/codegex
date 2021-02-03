import regex

from patterns.models.detectors import Detector
from patterns.models.bug_instance import BugInstance
from patterns.models import priorities


class SuspiciousCollectionMethodDetector(Detector):
    def __init__(self):
        self.pattern = regex.compile(
            r'(\b\w[\w.]*(?P<aux1>\((?:[^()]++|(?&aux1))*\))*+)\s*\.\s*((?:remove|contains|retain)(?:All)?)\s*\(\s*([\w.]+(?&aux1)*)\s*\)')
        Detector.__init__(self)

    def match(self, context):
        line_content = context.cur_line.content
        if not any(method in line_content for method in ['remove', 'contains', 'retain']):
            return

        its = self.pattern.finditer(line_content.strip())

        for m in its:
            g = m.groups()
            obj_1 = g[0]
            method_name = g[2]
            obj_2 = g[3]

            if obj_1 == obj_2:
                pattern_type, description, priority = None, None, None
                if method_name == 'removeAll':
                    pattern_type = 'DMI_USING_REMOVEALL_TO_CLEAR_COLLECTION'
                    description = 'removeAll used to clear a collection'
                    priority = priorities.MEDIUM_PRIORITY
                elif method_name in ['containsAll', 'retainAll']:
                    pattern_type = 'DMI_VACUOUS_SELF_COLLECTION_CALL'
                    description = 'Vacuous call to collections'
                    priority = priorities.MEDIUM_PRIORITY
                elif method_name in ['contains', 'remove']:
                    pattern_type = 'DMI_COLLECTIONS_SHOULD_NOT_CONTAIN_THEMSELVES'
                    description = 'Collections should not contain themselves'
                    priority = priorities.HIGH_PRIORITY

                if pattern_type:
                    self.bug_accumulator.append(
                        BugInstance(pattern_type, priority, context.cur_patch.name, context.cur_line.lineno[1],
                                    description, sha=context.cur_patch.sha)
                    )
                    return
