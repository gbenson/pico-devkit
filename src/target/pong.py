import random

from math import sqrt

from engine import FPSRunner, PicoScroll


INSERT_COIN = object()
COUNTDOWN = object()
RUNNING = object()

ANY_BUTTON_DOWN = object()
ALL_BUTTONS_UP = object()


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
        self.ball = Ball()

        self.reset()

    def reset(self):
        self.state = INSERT_COIN
        self.draw_ball = False
        self.draw_field = False
        self.wait_for_button_press()

    def wait_for_button_press(self):
        self._awaiting_interaction = ANY_BUTTON_DOWN
        self._draw()

    def tick(self, delta_t):
        self._update(delta_t)
        if self._awaiting_interaction:
            return
        self._draw()

    def _update(self, delta_t):
        if self._awaiting_interaction is ANY_BUTTON_DOWN:
            if not any(b.is_pressed() for b in self.buttons):
                return
            self._awaiting_interaction = ALL_BUTTONS_UP
            return

        if self._awaiting_interaction is ALL_BUTTONS_UP:
            if any(b.is_pressed() for b in self.buttons):
                return
            self._awaiting_interaction = None
            self.draw_field = True
            self.countdown = 2
            self.state = COUNTDOWN
            return

        for p in self.players:
            p.update(delta_t)

        if self.state is COUNTDOWN:
            self.countdown -= delta_t
            if self.countdown > 0:
                return
            self.ball.reset()
            self.draw_ball = True
            self.state = RUNNING
            return

        ball = self.ball
        ball.update(delta_t, self.players)
        if ball.x + ball.radius < 0:
            print("player[1] wins!")
            self.reset()
        elif ball.x - ball.radius > 16:
            print("player[0] wins!")
            self.reset()

    def _draw(self):
        d = self.display
        set_pixel = d.set_pixel
        d.clear()
        try:
            for p in self.players:
                p.draw(set_pixel)
            if self.draw_ball:
                self.ball.draw(set_pixel)
            if self.draw_field:
                for y in (0, 2, 4, 6):
                    set_pixel(8, y, 128)
        finally:
            d.show()


class Player:
    def __init__(self, up_button, down_button, column):
        self.x = column
        self.y = 3.5  # bat at [2.5..4.5)
        self.up = up_button
        self.down = down_button
        self.speed = 12

    def is_at(self, y):
        cy = self.y
        return y >= cy - 1 and y <= cy + 1

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


class Ball:
    def __init__(self, radius=0.5):
        self.radius = radius
        self.reset()

    def reset(self, speed=10):
        self.x = 8.5  # ball at [8..9)
        margin = self.radius + 0.1
        self.y = random.uniform(margin, 7 - margin)
        rx = random.choice((0, 16)) - self.x
        ry = random.uniform(-6, 12) - self.y
        scale = speed / sqrt(rx * rx + ry * ry)
        self.vx = rx * scale
        self.vy = ry * scale

    def update(self, dt, players):
        radius = self.radius
        # top and bottom edges of screen
        top = radius
        bottom = 7 - radius
        # left and right edges of paddles
        left = 1 + radius
        right = 16 - radius

        while dt > 0:
            dx = self.vx * dt
            dy = self.vy * dt

            x = self.x + dx
            y = self.y + dy

            # top edge?
            excess_dy = y - top
            if excess_dy < 0:
                excess_dt = dt * excess_dy / dy
                self.x += self.vx * (dt - excess_dt)
                self.y = top
                self.vy *= -1
                dt = excess_dt
                continue

            # bottom edge?
            excess_dy = y - bottom
            if excess_dy > 0:
                excess_dt = dt * excess_dy / dy
                self.x += self.vx * (dt - excess_dt)
                self.y = bottom
                self.vy *= -1
                dt = excess_dt
                continue

            # left player
            excess_dx = x - left
            if excess_dx < 0:
                excess_dt = dt * excess_dx / dx
                hit_y = self.y + self.vy * (dt - excess_dt)
                if players[0].is_at(hit_y):
                    self.x = left
                    self.y = hit_y
                    self.vx *= -1
                    # english?
                    dt = excess_dt
                    continue

            # right player
            excess_dx = x - right
            if excess_dx > 0:
                excess_dt = dt * excess_dx / dx
                hit_y = self.y + self.vy * (dt - excess_dt)
                if players[1].is_at(hit_y):
                    self.x = right
                    self.y = hit_y
                    self.vx *= -1
                    # english?
                    dt = excess_dt
                    continue

            self.x = x
            self.y = y
            break

    def draw(self, set_pixel):
        x = self.x - 0.5
        y = self.y - 0.5

        # A B
        # C D

        # xbd is the x of the B and D, so xbd<0 means everything's offscreen.
        # The +2,-1 stuff is because python `int` rounds towards zero but we
        # need rounding like `math.floor`.  if xbd<0 then 1<=vac<2 which is
        # broken.
        xbd = int(x + 2) - 1
        if xbd < 0:
            return
        xac = xbd - 1
        vbd = x - xac
        vac = 1 - vbd

        ycd = int(y + 2) - 1
        if ycd < 0:
            return
        yab = ycd - 1
        vcd = y - yab
        vab = 1 - vcd

        for x, y, v in (
                (xac, yab, vac * vab),
                (xbd, yab, vbd * vab),
                (xac, ycd, vac * vcd),
                (xbd, ycd, vbd * vcd)):
            if 0 <= x < 17 and 0 <= y < 7:
                set_pixel(x, y, v * 255)


def main(*args, **kwargs):
    Game(*args, **kwargs).run()


if __name__ == "__main__":
    main()
