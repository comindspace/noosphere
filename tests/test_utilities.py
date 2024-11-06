from pytest import *

from package.utilities import *

@mark.parametrize('string, expected', [
    (None, True),
    ('', True),
    (' ', True),
    ('\t', True),
    ('\n', True),
    ('a', False),
])
def test_is_blank(string: str, expected: bool) -> None:
    assert expected is is_blank(string)
