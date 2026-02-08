from unittest.mock import Mock

import pytest

from devkit.pygame import PicoScroll

TEST_BITMAP = b"^E^@>*\x14\x00A\x006\x086\x01]Q="


def test_basics(pygame: Mock) -> None:
    scroll = PicoScroll()
    scroll.show_bitmap_1d(bytearray(TEST_BITMAP), 255, 0)

    # these two pixels won't be this if the image is mirrored or flipped
    assert scroll._fb[2] == 0
    assert scroll._fb[19] == 255

    scroll.show_bitmap_1d(bytearray(TEST_BITMAP), 255, -1)
    assert scroll._fb[2] == 255
    assert scroll._fb[19] == 0

    scroll.show_bitmap_1d(bytearray(TEST_BITMAP), 255, 3)
    assert scroll._fb[2] == 0
    assert scroll._fb[19] == 255


def test_errors(pygame: Mock) -> None:
    scroll = PicoScroll()
    with pytest.raises(TypeError):
        scroll.show_bitmap_1d(TEST_BITMAP, 255, 0)
