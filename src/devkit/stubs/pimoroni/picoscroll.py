"""Stub for the `picoscroll` MicroPython module from Pimoroni.

Code for interfacing with the Pimoroni Pico Scroll Pack,
a 17×7 white LED matrix with four buttons for the Raspberry Pi Pico:
 - https://shop.pimoroni.com/products/pico-scroll-pack

The original module's source and documentation are here:
 - https://github.com/pimoroni/pimoroni-pico/tree/main/micropython/modules/pico_scroll

The original module is "Copyright (C) 2021 Pimoroni Ltd" and
was released under the MIT License:
 - https://github.com/pimoroni/pimoroni-pico/blob/main/LICENSE
 - https://opensource.org/license/MIT

The documentation strings in this module were derived from the
original module's "README.md".
"""
from typing import ClassVar


class PicoScroll:
    WIDTH: ClassVar[int] = 17
    HEIGHT: ClassVar[int] = 7

    BUTTON_A: ClassVar[int] = 0
    BUTTON_B: ClassVar[int] = 1
    BUTTON_X: ClassVar[int] = 2
    BUTTON_Y: ClassVar[int] = 3

    def get_width(self) -> int:
        """Return the width of the Scroll Pack in pixels.
        """
        return self.WIDTH

    def get_height(self) -> int:
        """Return the height of the Scroll Pack in pixels.
        """
        return self.HEIGHT

    def set_pixel(self, x: int, y: int, level: int) -> None:
        """Set the pixel `(x, y)` to a brightness level specified by the
        `v` parameter.  The value of `v` must be 0-255.  Changes will not
        be visible until `show()` is called.
        """
        raise NotImplementedError

    def set_pixels(self, image: bytearray) -> None:
        """Sets all pixels at once from a `bytearray` image indexed
        as `y * picoscroll.get_width() + x`, containing brightness
        levels between 0 and 255. Changes will not be visible until
        `show()` is called.

        ```python
        image = bytearray(0 for j in range(width * height))
        picoscroll.set_pixels(image)
        ```
        """
        raise NotImplementedError

    def show_text(self, text: str | bytearray, level: int, offset: int) -> None:
        """Show a text string with given brightness and offset, allowing you
        to scroll text across the display. Can also be passed a `bytearray`.
        Font is 5x7 pixels, with a 1 pixel space between characters, so to
        scroll a phrase across the entire display involves offsets from -17
        pixels to `6 x len(str)`:

        ```python
        word = "Hello, world!"
        l = len(word) * 6
        for j in range(-17, l):
            picoscroll.show_text(word, 8, j)
            picoscroll.show()
            time.sleep(0.1)
        ```

        The full 256 characters can be displayed with:

        ```python
        b = bytearray(range(256))
        for j in range(256*6):
            picoscroll.show_text(b, 8, j)
            picoscroll.show()
            time.sleep(0.1)
        ```
        """
        raise NotImplementedError

    def scroll_text(self, text: str | bytearray, level: int, delay_ms: int) -> None:
        """Scroll a string across the picoscroll, starting off the right
        hand side, to the left, with a given delay in ms.

        ```python
        picoscroll.scroll_text("Hello, world!", 8, 100)
        ```

        The full 256 characters can be displayed with:

        ```python
        b = bytearray(range(256))
        picoscroll.scroll_text(b, 8, 100)
        ```
        """
        raise NotImplementedError

    def show_bitmap_1d(self, bitmap: bytearray, level: int, offset: int) -> None:
        """Show a bitmap stored as the 7 least significant bits of
        bytes in a `bytearray`, top-down. Individual pixels are set to
        the given brightness based on individual bit values, with the
        view defined by the offset and the width of the scroll (i.e.
        17 columns). Changes will not be visible until `show()` is called.

        ```python
        bitmap = bytearray(j for j in range 127)
        for offset in range(-17, 127):
            picoscroll.show_bitmap_1d(bitmap, 16, offset)
            picoscroll.show()
        ```

        will scroll a binary counter across the display (i.e. show `0x00`
        to `0x7f` in binary).
        """
        raise NotImplementedError

    def show(self) -> None:
        """Push pixel data from the Pico to the Scroll Pack.  Until this
        function is called any `set_pixel` or `clear` calls won't have any
        visible effect.
        """
        raise NotImplementedError

    def clear(self) -> None:
        """Sets the brightness of all pixels to `0`.  Will not visibly
        take effect until `show` is called.
        """
        raise NotImplementedError

    def is_pressed(self, b: int) -> bool:
        """Checks if a specified button is currently being pressed.
        Valid values of `b` are `picoscroll.BUTTON_A`,
        `picoscroll.BUTTON_B`, `picoscroll.BUTTON_X`, or
        `picoscroll.BUTTON_Y`, which match the silkscreen
        labels beside the buttons on the board.
        """
        raise NotImplementedError


WIDTH = PicoScroll.WIDTH
HEIGHT = PicoScroll.HEIGHT

BUTTON_A = PicoScroll.BUTTON_A
BUTTON_B = PicoScroll.BUTTON_B
BUTTON_X = PicoScroll.BUTTON_X
BUTTON_Y = PicoScroll.BUTTON_Y


__all__ = [
    "PicoScroll",
    "WIDTH",
    "HEIGHT",
    "BUTTON_A",
    "BUTTON_B",
    "BUTTON_X",
    "BUTTON_Y",
]
