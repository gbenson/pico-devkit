from utime import ticks_us, ticks_diff, sleep_us

_S_TO_US = 1_000_000
_US_TO_S = 1 / _S_TO_US


class Clock:
    def __init__(self, max_framerate=60):
        self.max_framerate = max_framerate
        self._last_tick = None

    @property
    def max_framerate(self):
        min_interval = self.min_interval
        if min_interval:
            return 1 / min_interval

    @max_framerate.setter
    def max_framerate(self, max_framerate):
        if max_framerate:
            self.min_interval = 1 / max_framerate
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

    def advance(self):
        return self.advance_us() * _US_TO_S

    def advance_us(self):
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
