"""Stub for the `time` MicroPython module.

(It's called `utime` because MicroPython allows importing built-in
modules by appending a "u" to the start of its name.  This is
deprecated, but I'm using it to avoid having to insert functions
into CPython's `time` module without breaking flake8 etc.)

The original module's source and documentation are here:
 - https://github.com/micropython/micropython/blob/master/extmod/modtime.c
 - https://github.com/micropython/micropython/blob/master/docs/library/time.rst

MicroPython is "Copyright (c) 2013-2025 Damien P. George" and
was released under the MIT License:
 - https://github.com/micropython/micropython/blob/master/LICENSE
 - https://opensource.org/license/MIT

The documentation strings in this module were derived from the
original module's documentation.
"""
from time import monotonic_ns, sleep


def sleep_us(us: int) -> None:
    """Suspend execution for the given number of microseconds.

    This function attempts to provide an accurate delay of at least
    `us` microseconds, but it may take longer if the system has other
    higher priority processing to perform.
    """
    if not isinstance(us, int):
        raise TypeError(type(us).__name__)
    if us < 0:
        raise ValueError(f"us={us}")
    sleep(us / 1_000_000)


def ticks_us() -> int:
    """Returns an increasing microsecond counter with an arbitrary
    reference point, that wraps around after some value.
    """
    return monotonic_ns() // 1000


def ticks_diff(ticks1: int, ticks2: int) -> int:
    """Calculate the ticks difference between values returned by
    `ticks_us()`.

    The argument order is the same as for the subtraction operator, i.e.
   `ticks_diff(ticks1, ticks2)` has the same meaning as `ticks1 - ticks2`.
    """
    return ticks1 - ticks2
