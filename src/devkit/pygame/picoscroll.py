from collections.abc import Container

import pygame

from ..stubs.pimoroni.picoscroll import PicoScroll as _PicoScroll


class PicoScroll(_PicoScroll):
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


def _raise_unless_valid_int(
        value: int,
        name: str,
        valid_values: Container[int],
) -> None:
    if not isinstance(value, int):
        raise TypeError(f"{name}={value}")
    if value not in valid_values:
        raise ValueError(f"{name}={value}")
