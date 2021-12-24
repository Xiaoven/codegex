import re
import os


def snake_to_camel(word):
    return ''.join(x.capitalize() for x in word.split('_'))


if __name__ == '__main__':
    p_detector = re.compile(r'class\s*([^\s()]+)\(Detector\)')
    p = re.compile(r'[\'"]([A-Z0-9]+_+[A-Z_0-9]+)[\'"]')
    detector_path = os.path.join(os.getcwd(), 'patterns/detect')
    all_pattern_set = set()     # Pattern names of Codegex, including synthetic patterns
    # ========= gen_detectors.py is used to register detectors, i.e. let engine knows the detectors in
    file_names = list()         # File names of detectors in Codegex, used to update gen_detectors.py
    detector_names = list()     # class names of detectors in Codegex, used to update gen_detectors.py
    import_list = list()        # used to update the imports of gen_detectors.py

    for filename in os.listdir(detector_path):
        path = os.path.join(detector_path, filename)
        if not os.path.isfile(path):
            continue

        strip_filename = filename[:-3]  # Remove '.py'

        camel_name = snake_to_camel(strip_filename)
        file_names.append(camel_name)

        import_stmt = None

        with open(path, 'r') as f:
            content = f.read()
            pattern_list = p.findall(content)
            if pattern_list:
                all_pattern_set.update(pattern_list)

            detectors = p_detector.findall(content)
            if detectors:
                tmp_str = ', '.join(detectors)
                import_stmt = f'from codegex.detect.{strip_filename} import {tmp_str}\n'
                for name in detectors:
                    detector_names.append(f'"{name}": {name}')

        if import_stmt:
            import_list.append(import_stmt)

    # print('[Number of detector files in Codegex]', len(file_names))
    # print('[Number of original patterns in Codegex]', len(all_pattern_set))
    # print('[Number of detector classes in codegex]', len(detector_names))

    # print(all_pattern_set)

    # print visitors which is used to config SpotBugs maven plugins to decide to run detectors in which files
    visitors = list()
    for name in file_names:
        if name == 'FindSelfAssignment':
            visitors.append('FindFieldSelfAssignment')
            visitors.append('FindLocalSelfAssignment2')
        elif name == 'FindSelfComparison':
            visitors.append('FindSelfComparison')
            visitors.append('FindSelfComparison2')
        elif name == 'FindBadCast':
            visitors.append('FindBadCast2')
        else:
            visitors.append(name)
    # print(','.join(visitors))


    # # This writing operation should be enabled only when the old gen_detectors.py is not maintained after implementing new patterns
    # with open('gen_detectors.py', 'w') as f:
    #     if import_list:
    #         f.writelines(import_list)
    #     if detector_names:
    #         f.write('\nDETECTOR_DICT = {\n    ' + ',\n    '.join(detector_names) + '\n}')

    # patterns_to_write matches codegex patterns to spotbugs patterns, and is used to generate warning filter files in comparison experiment with spotbugs
    patterns_to_write = set()
    for pattern in all_pattern_set:
        if pattern == 'SA_SELF_ASSIGNMENT':
            patterns_to_write.add('SA_FIELD_SELF_ASSIGNMENT')
            patterns_to_write.add('SA_LOCAL_SELF_ASSIGNMENT')
        elif pattern == 'SA_SELF_COMPARISON':
            patterns_to_write.add('SA_FIELD_SELF_COMPARISON')
            patterns_to_write.add('SA_LOCAL_SELF_COMPARISON')
        elif pattern == 'SA_SELF_COMPUTATION':
            patterns_to_write.add('SA_FIELD_SELF_COMPUTATION')
            patterns_to_write.add('SA_LOCAL_SELF_COMPUTATION')
        elif pattern == 'SA_DOUBLE_ASSIGNMENT':
            patterns_to_write.add('SA_FIELD_DOUBLE_ASSIGNMENT')
            patterns_to_write.add('SA_LOCAL_DOUBLE_ASSIGNMENT')
        else:
            patterns_to_write.add(pattern)

    print(f'Number of implemented SpotBugs patterns by Codegex = {len(patterns_to_write)}')
    print('\n'.join(list(patterns_to_write)))

    # # Generate warning filter files used in comparison experiment with spotbugs
    # with open('spotbugs-includeFilter.xml', 'w') as f:
    #     f.write('<FindBugsFilter>\n')
    #     for pattern in patterns_to_write:
    #         f.write(f'\t<Match>\n\t\t<Bug pattern="{pattern}"/>\n\t</Match>\n')
    #     f.write('</FindBugsFilter>')
