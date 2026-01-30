from engine import Clock
from picoscroll import PicoScroll


class Game:
    def __init__(self, scroll=None, max_framerate=60, gamma=3):
        self._scroll = scroll or PicoScroll()
        self._clock = Clock(max_framerate)
        self._gamma = gamma

    def reset(self):
        self.ball = 0, 0

    def tick(self):
        x, y = self.ball
        self.set_pixel(x, y, 0)
        n = y * 17 + x
        y, x = divmod(n + 1, 17)
        y = y if y < 7 else 0
        self.set_pixel(x, y, 255)
        self.ball = x, y

    def run(self):
        self.reset()
        while True:
            self.time = self._clock.advance()
            self.tick()
            self._scroll.show()

    def set_pixel(self, x, y, v):
        v = round(255 * ((v / 255) ** self._gamma))
        self._scroll.set_pixel(x, y, v)


def main(*args, **kwargs):
    app = Game(*args, **kwargs)
    app.run()


if __name__ == "__main__":
    main()
