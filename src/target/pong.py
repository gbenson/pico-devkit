from engine import FPSRunner, PicoScroll


class Game(FPSRunner):
    def __init__(self, scroll=None, **kwargs):
        super().__init__(**kwargs)

        scroll = scroll or PicoScroll()
        self.display = scroll.display
        self.buttons = buttons = scroll.buttons

        self.players = [
            Player(buttons.A, buttons.B, 0),
            Player(buttons.X, buttons.Y, 16),
        ]

    def tick(self, delta_t):
        self._update(delta_t)
        self._draw()

    def _update(self, delta_t):
        for p in self.players:
            p.update(delta_t)

    def _draw(self):
        d = self.display
        set_pixel = d.set_pixel
        d.clear()
        try:
            for p in self.players:
                p.draw(set_pixel)
        finally:
            d.show()


class Player:
    def __init__(self, up_button, down_button, column):
        self.x = column
        self.y = 3.5  # bat at [2.5..4.5)
        self.up = up_button
        self.down = down_button
        self.speed = 12

    def update(self, delta_t):
        move_up = self.up.is_pressed()
        move_down = self.down.is_pressed()
        if not (move_up ^ move_down):
            return
        if move_up:
            y = self.y
            y -= self.speed * delta_t
            y = max(y, 1)  # bat at [0..2)
            self.y = y
        else:  # move down
            y = self.y
            y += self.speed * delta_t
            y = min(y, 6)  # bat at [5..7)
            self.y = y

    def draw(self, set_pixel):
        x = self.x
        y = self.y

        y1 = int(y)
        y0 = y1 - 1
        y2 = y1 + 1
        v2 = (y - y1) * 255

        if y0 >= 0:
            v0 = 255 - v2
            set_pixel(x, y0, v0)
        set_pixel(x, y1, 255)
        if y2 < 7:
            set_pixel(x, y2, v2)


def main(*args, **kwargs):
    Game(*args, **kwargs).run()


if __name__ == "__main__":
    main()
