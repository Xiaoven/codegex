from codegex.utils.utils import *


def test_get_string_ranges():
    assert get_string_ranges('""')[0] == (0, 2)
    assert get_string_ranges(
        '''print("a normal string");
        print("she said \\"yes\\"");
        print("she said \\"yes\\" and smiled");
        ''') == [(6, 23), (40, 58), (75, 104)]


def test_get_string_ranges_01():
    assert get_string_ranges('seqDetails[1].trim().equals("")')[0] == (28, 30)