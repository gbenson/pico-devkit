import pytest

import picoscroll


@pytest.mark.parametrize(
    "item", (
        picoscroll,
        picoscroll.PicoScroll,
        picoscroll.PicoScroll(),
    ))
@pytest.mark.parametrize(
    "attr,expect_value", {
        "BUTTON_A": 0,
        "BUTTON_B": 1,
        "BUTTON_X": 2,
        "BUTTON_Y": 3,
        "WIDTH": 17,
        "HEIGHT": 7,
    }.items())
def test_constants(item, attr, expect_value):
    assert hasattr(item, attr)
    value = getattr(item, attr)
    assert isinstance(value, int)
    assert value == expect_value


def test_getters():
    scroll = picoscroll.PicoScroll()
    assert scroll.get_width() == 17
    assert scroll.get_height() == 7
