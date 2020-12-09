import re
import os


def snake_to_camel(word):
    return ''.join(x.capitalize() for x in word.split('_'))


if __name__ == '__main__':
    p_detector = re.compile(r'class\s*([^\s()]+)\((?:Parent)?Detector\)')
    p = re.compile(r'[\'"]([A-Z_0-9]+)[\'"]')
    detector_path = os.path.join(os.getcwd(), 'patterns/detect')
    all_pattern_set = set()
    file_names = list()
    detector_names = list()

    for filename in os.listdir(detector_path):
        camel_name = snake_to_camel(filename.rstrip('.py'))
        file_names.append(camel_name)

        path = os.path.join(detector_path, filename)
        if not os.path.isfile(path):
            continue
        with open(path, 'r') as f:
            content = f.read()
            pattern_list = p.findall(content)
            if pattern_list:
                all_pattern_set.update(pattern_list)

            m = p_detector.search(content)
            if m:
                detector_names.append(m.groups()[0] + '()')

    print('[Class names]', ','.join(file_names))
    print('[Number of patterns]', len(all_pattern_set))
    print('[Pattern names]', ','.join(all_pattern_set))
    print('[Number of Detectors]', len(detector_names))
    print('[Detectors]\n', ','.join(detector_names))

