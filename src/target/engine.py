from picoscroll import PicoScroll as _PicoScroll
from utime import ticks_us, ticks_diff, sleep_us

_S_TO_US = 1_000_000
_US_TO_S = 1 / _S_TO_US


class RateLimiter:
    def __init__(self, max_rate=None):
        self.max_rate = max_rate
        self._last_tick = None

    @property
    def max_rate(self):
        min_interval = self.min_interval
        if min_interval:
            return 1 / min_interval

    @max_rate.setter
    def max_rate(self, max_rate):
        if max_rate:
            self.min_interval = 1 / max_rate
        else:
            self.min_interval = None

    @property
    def min_interval(self):
        return self.min_interval_us * _US_TO_S

    @min_interval.setter
    def min_interval(self, value):
        if not value or value <= 0:
            value = 0
        self.min_interval_us = value * _S_TO_US

    @property
    def min_interval_us(self):
        return self._min_interval_us

    @min_interval_us.setter
    def min_interval_us(self, value):
        if not value or value <= 0:
            value = 0
        self._min_interval_us = value

    def wait(self):
        return self.wait_us() * _US_TO_S

    def wait_us(self):
        self._maybe_wait()
        this_tick = ticks_us()
        self._last_tick = this_tick
        return this_tick

    def _maybe_wait(self):
        min_interval = self._min_interval_us
        if not min_interval:
            return
        last_tick = self._last_tick
        if not last_tick:
            return
        this_tick = ticks_us()
        interval = ticks_diff(this_tick, last_tick)
        time_to_wait = round(min_interval - interval)
        if time_to_wait < 0:
            return
        sleep_us(time_to_wait)


class FrameTicker:
    def __init__(self, *, limiter=None, max_framerate=60):
        self._limiter = limiter or RateLimiter()
        self.max_framerate = max_framerate

    @property
    def max_framerate(self):
        return self._limiter.max_rate

    @max_framerate.setter
    def max_framerate(self, max_framerate):
        self._limiter.max_rate = max_framerate

    def run(self):
        last_time = self._limiter.wait()
        while True:
            time = self._limiter.wait()
            self.tick(time - last_time)
            last_time = time


class Display:
    def __init__(self, provider, gamma=1):
        self.gamma = gamma

        self.width = provider.get_width()
        self.height = provider.get_height()
        self.size = self.width, self.height

        self._set_pixel = provider.set_pixel
        self.clear = provider.clear
        self.show = provider.show

    def set_pixel(self, x, y, v):
        v = round(255 * ((v / 255) ** self.gamma))
        self._set_pixel(x, y, v)


class Buttons:
    def __init__(self, provider, **buttons):
        self._all = []
        for attr, code in buttons.items():
            button = Button(provider, code)
            setattr(self, attr, button)
            self._all.append(button)

    def __iter__(self):
        return iter(self._all)


class Button:
    def __init__(self, provider, code):
        self._provider = provider
        self._button = code

    def is_pressed(self):
        return self._provider.is_pressed(self._button)


class PicoScroll:
    def __init__(self, scroll=None, gamma=3):
        scroll = scroll or _PicoScroll()
        self.display = Display(scroll, gamma)
        self.buttons = Buttons(
            scroll,
            A=scroll.BUTTON_A,
            B=scroll.BUTTON_B,
            X=scroll.BUTTON_X,
            Y=scroll.BUTTON_Y,
        )
