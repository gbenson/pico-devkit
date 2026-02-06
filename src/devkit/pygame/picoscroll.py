from collections.abc import Container
from typing import ClassVar

import pygame

from ..stubs.pimoroni.picoscroll import PicoScroll as _PicoScroll


class PicoScroll(_PicoScroll):
    _KEYMAP: ClassVar[dict[int, int]] = {
        pygame.K_a: _PicoScroll.BUTTON_A,
        pygame.K_b: _PicoScroll.BUTTON_B,
        pygame.K_x: _PicoScroll.BUTTON_X,
        pygame.K_y: _PicoScroll.BUTTON_Y,

        # for A, {Z,C} = up, down
        pygame.K_z: _PicoScroll.BUTTON_B,
        pygame.K_c: _PicoScroll.BUTTON_B,

        # for {J,K,L}, M = up, down
        pygame.K_j: _PicoScroll.BUTTON_X,
        pygame.K_k: _PicoScroll.BUTTON_X,
        pygame.K_l: _PicoScroll.BUTTON_X,
        pygame.K_m: _PicoScroll.BUTTON_Y,
    }

    def __init__(self, *, window_title: str = "Pico Scroll", gamma: float = 3):
        if not pygame.get_init():
            pygame.init()

        w, h = self._get_size()

        display_info = pygame.display.Info()
        self._scale = display_info.current_w // (w * 3)
        display_size = w * self._scale, h * self._scale
        self._display = pygame.display.set_mode(display_size)

        pygame.display.set_caption(window_title)

        self._num_pixels = w * h
        self._fb = bytearray()
        self._gamma = 1 / gamma

        self._is_pressed = [False] * 4

        self.clear()
        self.show()

    def _get_size(self) -> tuple[int, int]:
        return self.get_width(), self.get_height()

    def clear(self) -> None:
        self._fb = bytearray(self._num_pixels)

    def set_pixel(self, x: int, y: int, level: int) -> None:
        width, height = self._get_size()

        _raise_unless_valid_int(x, "x", range(width))
        _raise_unless_valid_int(y, "y", range(height))
        _raise_unless_valid_int(level, "level", range(256))

        self._fb[y * width + x] = level

    def show_bitmap_1d(self, bitmap: bytearray, level: int, offset: int) -> None:
        if not isinstance(bitmap, bytearray):
            raise TypeError("object with buffer protocol required")

        columns = range(len(bitmap))
        width, height = self._get_size()
        for x in range(width):
            if (i := offset + x) in columns:
                col = bitmap[i]
            else:
                col = 0
            for y in range(height):
                self.set_pixel(x, y, level if col & 1 else 0)
                col >>= 1

    def show(self) -> None:
        surface = self._display
        gamma = self._gamma
        scale = self._scale
        width, height = self._get_size()

        rect = pygame.Rect(0, 0, scale, scale)
        for y in range(height):
            rect.y = y * scale
            for x in range(width):
                raw_v = self._fb[y * width + x]
                v = round(255 * ((raw_v / 255) ** gamma))
                rect.x = x * scale
                pygame.draw.rect(surface, (v, v, v), rect)

        pygame.display.flip()

    def is_pressed(self, button: int) -> bool:
        self._handle_events()
        return self._is_pressed[button]

    def _handle_events(self) -> None:
        for event in pygame.event.get():
            match event.type:
                case pygame.QUIT:
                    raise SystemExit  # pragma: no cover
                case pygame.KEYDOWN:
                    self._handle_keyevent(event.key, True)
                case pygame.KEYUP:
                    if event.key == pygame.K_q:
                        raise SystemExit  # pragma: no cover
                    self._handle_keyevent(event.key, False)

    def _handle_keyevent(self, keycode: int, is_pressed: bool) -> None:
        button = self._KEYMAP.get(keycode)
        if button is None:
            return
        self._is_pressed[button] = is_pressed


def _raise_unless_valid_int(
        value: int,
        name: str,
        valid_values: Container[int],
) -> None:
    if not isinstance(value, int):
        raise TypeError(f"{name}={value}")
    if value not in valid_values:
        raise ValueError(f"{name}={value}")
