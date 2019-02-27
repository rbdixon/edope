import pytest

from edope.epo import LastVal
from math import floor, ceil


@pytest.mark.parametrize(
    'seq, avg', [[[1, 1, 1, 1, 1], 1], [[1, 2], 2], [list(range(0, 20)), 14], [[], 0]]
)
def test_lastval_avg(seq, avg):
    lv = LastVal()

    for v in seq:
        lv.append(v)
        assert len(lv) <= 10

    val = lv.avg()
    assert val >= floor(avg * 0.9)
    assert val <= ceil(avg * 1.1)


def test_max():
    lv = LastVal([0xFFFE, 0xFFFF])

    for x in range(0, 100):
        assert lv.avg() <= 0xFFFF
