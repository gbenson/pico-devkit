from typing import Any
from unittest.mock import Mock, NonCallableMock

import pytest

import pygame as _pygame

from pygame import Rect

from devkit.pygame import picoscroll as module


@pytest.fixture
def pygame(monkeypatch: pytest.MonkeyPatch) -> Mock:
    pygame = NonCallableMock()

    display = object()

    def checked_draw_rect(surface: Any, color: Any, rect: Rect) -> None:
        assert surface is display
        assert rect.w == 37
        assert rect.h == 37

    DIRECT_ATTRS = "K_a K_b K_q K_x K_y KEYUP KEYDOWN QUIT".split()
    for attr in DIRECT_ATTRS:
        setattr(pygame, attr, getattr(_pygame, attr))

    pygame.get_init.return_value = False
    pygame.init.return_value = (5, 0)
    pygame.display.Info.return_value = NonCallableMock()
    pygame.display.Info.return_value.current_w = 1913
    pygame.display.set_mode.return_value = display
    pygame.Rect = Rect
    pygame.draw.rect = checked_draw_rect

    assert len(pygame.mock_calls) == 0  # sanity

    with monkeypatch.context() as mp:
        mp.setattr(module, "pygame", pygame)
        yield pygame
