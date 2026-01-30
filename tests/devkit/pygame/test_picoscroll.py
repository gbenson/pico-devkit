import logging

from dataclasses import dataclass
from time import time
from typing import Any, Optional
from unittest.mock import Mock, NonCallableMock, patch

import pytest

from pygame import Rect

from devkit.pygame import PicoScroll
from target.pong import main

logger = logging.getLogger(__name__)
d = logger.info


# Tests

@patch("devkit.pygame.picoscroll.pygame")
def test_set_pixel(pygame: Mock) -> None:
    _common_setup(pygame)
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


@patch("devkit.pygame.picoscroll.pygame")
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
def test_set_pixel_errors(
        pygame: Mock,
        args: tuple[Any],
        expect_exc_type: type[Exception],
        expect_exc_message: str,
) -> None:
    _common_setup(pygame)
    scroll = PicoScroll()
    with pytest.raises(expect_exc_type) as e:
        scroll.set_pixel(*args)
    assert str(e.value) == expect_exc_message


@patch("devkit.pygame.picoscroll.pygame")
def test_pong_e2e(pygame: Mock) -> None:
    _common_setup(pygame)

    deadliner = Deadliner(timeout=1)
    pygame.display.flip = deadliner
    assert len(pygame.mock_calls) == 0  # sanity

    try:
        start_time = time()
        with pytest.raises(DeadlineExceeded):
            main()
    finally:
        d(f"ran for {time() - start_time:.2f}s")
        d(f"len(pygame.mock_calls) = {len(pygame.mock_calls)}")
        for i, call in enumerate(pygame.mock_calls[:20]):
            d(f"call {i+1}: {call}")

    assert len(pygame.mock_calls) == 5

    pygame.init.assert_called_once_with()
    pygame.display.set_mode.assert_called_once_with((629, 259))
    pygame.display.set_caption.called_once_with("Pico Scroll")

    num_frames = deadliner.num_calls
    d(f"num_frames={num_frames}")
    assert 55 < num_frames < 65  # it targets 60fps


# Helpers

def _common_setup(pygame: Mock):
    display = object()

    def checked_draw_rect(surface: Any, color: Any, rect: Rect) -> None:
        assert surface is display
        assert rect.w == 37
        assert rect.h == 37

    pygame.get_init.return_value = False
    pygame.init.return_value = (5, 0)
    pygame.display.Info.return_value = NonCallableMock()
    pygame.display.Info.return_value.current_w = 1913
    pygame.display.set_mode.return_value = display
    pygame.Rect = Rect
    pygame.draw.rect = checked_draw_rect

    assert len(pygame.mock_calls) == 0  # sanity


@dataclass
class Deadliner:
    timeout: Optional[float] = None
    deadline: Optional[float] = None
    num_calls: int = 0

    def __call__(self) -> None:
        self.num_calls += 1
        if self.deadline is not None:
            if time() > self.deadline:
                raise DeadlineExceeded
        elif self.timeout is not None:
            self.deadline = time() + self.timeout


class DeadlineExceeded(TimeoutError):
    pass
