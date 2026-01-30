import pytest

from utime import sleep_us


def test_sleep_us():
    sleep_us(1)
    sleep_us(0)
    with pytest.raises(TypeError):
        sleep_us(1.0)
    with pytest.raises(ValueError):
        sleep_us(-1)
