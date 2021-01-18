import glob
from os import path

if __name__ == '__main__':
    paths = glob.glob('PullRequests/java/links/**/*.csv', recursive=True)

    total_link_cnt = 0
    missing_file_cnt = 0
    link_dic = dict()

    for p in paths:
        with open(p, 'r') as f:
            for line in f:
                strip_line = line.strip()
                if strip_line:
                    total_link_cnt += 1

                    if strip_line in link_dic:
                        link_dic[strip_line] += 1
                        # print('[Duplicate]: ', line)
                    else:
                        link_dic[strip_line] = 0

                    file_path = strip_line.replace('https://api.github.com/repos/',
                                                   'PullRequests/java/files/') + '.json'

                    if not path.exists(file_path):
                        missing_file_cnt += 1
                        print('[Missing]: ', line)

    print('==========================')
    print(f'missing_file_cnt = {missing_file_cnt}')
    print(f'total_link_cnt = {total_link_cnt}')
    print(f'unique link = {len(link_dic)}')


