from picoscroll import PicoScroll


class Game:
    def __init__(self, scroll=None, gamma=3):
        self._scroll = scroll or PicoScroll()
        self._gamma = gamma

    def run(self):
        x = y = 0
        for n in range(17*7):
            self.set_pixel(x, y, 0)
            y, x = divmod(n, 17)
            self.set_pixel(x, y, 255)
            self._scroll.show()

    def set_pixel(self, x, y, v):
        v = round(255 * ((v / 255) ** self._gamma))
        self._scroll.set_pixel(x, y, v)


def main(*args, **kwargs):
    app = Game(*args, **kwargs)
    app.run()


if __name__ == "__main__":
    main()
