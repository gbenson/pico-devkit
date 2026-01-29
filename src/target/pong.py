from picoscroll import PicoScroll


class Game:
    def __init__(self, scroll=None):
        self._scroll = scroll or PicoScroll()

    def run(self):
        raise NotImplementedError


def main(*args, **kwargs):
    app = Game(*args, **kwargs)
    app.run()


if __name__ == "__main__":
    main()
