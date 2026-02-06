from typing import Any
from unittest.mock import Mock

import pytest

from devkit.pygame import PicoScroll


def test_basics(pygame: Mock) -> None:
    scroll = PicoScroll()

    # check the display starts clear
    assert sum(map(int, scroll._fb)) == 0

    # check setting the first pixel works
    scroll.set_pixel(0, 0, 192)
    assert scroll._fb[0] == 192
    assert sum(map(int, scroll._fb)) == 192

    # check setting the last pixel works
    scroll.set_pixel(16, 6, 218)
    assert scroll._fb[-1] == 218
    assert sum(map(int, scroll._fb)) == 410


@pytest.mark.parametrize(
    "args,expect_exc_type,expect_exc_message",
    (((-1, 0, 192), ValueError, "x=-1"),
     ((0, -1, 192), ValueError, "y=-1"),
     ((17, 0, 192), ValueError, "x=17"),
     ((0, 7, 192), ValueError, "y=7"),
     ((0, 0, -1), ValueError, "level=-1"),
     ((0, 0, 256), ValueError, "level=256"),
     ((0.0, 0, 192), TypeError, "x=0.0"),
     ((0, 0.0, 192), TypeError, "y=0.0"),
     ((0, 0, 192.0), TypeError, "level=192.0"),
     ))
def test_errors(
        pygame: Mock,
        args: tuple[Any],
        expect_exc_type: type[Exception],
        expect_exc_message: str,
) -> None:
    scroll = PicoScroll()
    with pytest.raises(expect_exc_type) as e:
        scroll.set_pixel(*args)
    assert str(e.value) == expect_exc_message
