from typing import Any

import pytest

from engine import FrameTicker


def test_default_limit() -> None:
    t = FrameTicker()
    assert t.max_framerate == 60


def test_init_with_limit() -> None:
    t = FrameTicker(max_framerate=23)
    assert t.max_framerate == 23


def test_set_limit() -> None:
    t = FrameTicker()
    t.max_framerate = 42
    assert t.max_framerate == 42


@pytest.mark.parametrize("framerate", (None, 0, 0.0, -1))
def test_init_unlimited(framerate: Any) -> None:
    t = FrameTicker(max_framerate=framerate)
    assert t.max_framerate is None


@pytest.mark.parametrize("framerate", (None, 0, 0.0, -1))
def test_set_unlimited(framerate: Any) -> None:
    t = FrameTicker()
    t.max_framerate = framerate
    assert t.max_framerate is None
