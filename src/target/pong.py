import random

from math import atan2, cos, pi, sin, sqrt

from engine import FPSRunner, PicoScroll


INSERT_COIN = object()
COUNTDOWN = object()
RUNNING = object()
PLAYER_SCORED = object()

ANY_BUTTON_DOWN = object()
ALL_BUTTONS_UP = object()


class Game(FPSRunner):
    DEBOUNCE = 0.25

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
        self.draw_field = True
        self.draw_players = True
        self.animation = None
        self.wait_for_button_press()

    def start_countdown(self, duration=2):
        self.state = COUNTDOWN
        self.draw_ball = False
        self.draw_field = False
        self.draw_players = True
        self.animation = CountdownAnimation()
        self.countdown = duration

    def congratulate(self, player):
        self.state = PLAYER_SCORED
        self.draw_ball = False
        self.draw_field = False
        self.draw_players = False
        self.animation = ScoreAnimation(not bool(player.x))
        self.wait_for_button_press()

    def wait_for_button_press(self):
        self._awaiting_interaction = ANY_BUTTON_DOWN
        self._debounce = self.DEBOUNCE
        self._draw()

    def tick(self, delta_t):
        self._update(delta_t)
        if self.state is INSERT_COIN:
            return
        self._draw()

    def _update(self, delta_t):
        if self.animation:
            self.animation.update(delta_t)

        if self._awaiting_interaction and (debounce := self._debounce):
            debounce -= delta_t
            if debounce > 0:
                self._debounce = debounce
                return
            self._debounce = None

        if self._awaiting_interaction is ANY_BUTTON_DOWN:
            if not any(b.is_pressed() for b in self.buttons):
                return
            self._awaiting_interaction = ALL_BUTTONS_UP
            return

        if self._awaiting_interaction is ALL_BUTTONS_UP:
            if any(b.is_pressed() for b in self.buttons):
                return
            self._awaiting_interaction = None
            if self.state is PLAYER_SCORED:
                self.reset()
            else:
                self.start_countdown()
            return

        for p in self.players:
            p.update(delta_t)

        if self.state is COUNTDOWN:
            self.countdown -= delta_t
            if self.countdown > 0:
                return
            self.animation = None
            self.ball.reset()
            self.draw_ball = True
            self.draw_field = True
            self.state = RUNNING
            return

        ball = self.ball
        ball.update(delta_t, self.players)
        if ball.x + ball.radius < 0:
            self.congratulate(self.players[1])
        elif ball.x - ball.radius > 16:
            self.congratulate(self.players[0])

    def _draw(self):
        d = self.display
        set_pixel = d.set_pixel
        d.clear()
        try:
            if self.animation:
                self.animation.draw(d)

            if self.draw_players:
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
        self.vy = 0

    def is_at(self, y):
        cy = self.y
        return y >= cy - 1.25 and y <= cy + 1.25

    def update(self, delta_t):
        move_up = self.up.is_pressed()
        move_down = self.down.is_pressed()
        if not (move_up ^ move_down):
            self.vy = 0
            return
        y0 = y1 = self.y
        if move_up:
            y1 -= self.speed * delta_t
            y1 = max(y1, 1)  # bat at [0..2)
        else:  # move down
            y1 += self.speed * delta_t
            y1 = min(y1, 6)  # bat at [5..7)
        self.y = y1

        # include a decaying component of last frame's speed in this
        # frame's speed; we have buttons, not a trackball, and we'd
        # have pretty much the same vy for every collision otherwise.
        self.vy = y1 - y0 + max(1 - delta_t, 0) * self.vy

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
    def __init__(self, radius=0.5, max_english=pi / 5):
        self.radius = radius
        self.max_english = max_english  # do not let it turn around!
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
        self.spin = 0

    def update(self, delta_t, players):
        radius = self.radius
        # top and bottom edges of screen
        top = radius
        bottom = 7 - radius
        # left and right edges of paddles
        left = 1 + radius
        right = 16 - radius

        dt = delta_t
        while dt > 0:
            # always be moving towards a player
            chk_vx = abs(self.vx)
            if chk_vx < 0.05:
                self.vx = random.uniform(-1, 1)
            elif chk_vx < 0.1:
                self.vx *= 1.1

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
                self._english()
                dt = excess_dt
                continue

            # bottom edge?
            excess_dy = y - bottom
            if excess_dy > 0:
                excess_dt = dt * excess_dy / dy
                self.x += self.vx * (dt - excess_dt)
                self.y = bottom
                self.vy *= -1
                self._english()
                dt = excess_dt
                continue

            # left player
            excess_dx = x - left
            if excess_dx < 0:
                excess_dt = dt * excess_dx / dx
                hit_y = self.y + self.vy * (dt - excess_dt)
                player = players[0]
                if player.is_at(hit_y):
                    self.x = left
                    self.y = hit_y
                    self.vx *= -1
                    self.spin -= player.vy
                    self._english()
                    if self.vx < 0:
                        self.vx *= -1  # move AWAY from the player!
                    dt = excess_dt
                    continue

            # right player
            excess_dx = x - right
            if excess_dx > 0:
                excess_dt = dt * excess_dx / dx
                hit_y = self.y + self.vy * (dt - excess_dt)
                player = players[1]
                if player.is_at(hit_y):
                    self.x = right
                    self.y = hit_y
                    self.vx *= -1
                    self.spin += player.vy
                    self._english()
                    if self.vx > 0:
                        self.vx *= -1  # move AWAY from the player!
                    dt = excess_dt
                    continue

            self.x = x
            self.y = y
            break

        k = min(delta_t, 0.1)
        self.spin *= (1 - k)  # decay
        kk = 1 + k * 0.02
        self.vx *= kk  # faster!
        self.vy *= kk

    def _english(self, spinfrac=0.6):
        spin = self.spin * spinfrac
        self.spin -= spin
        if spin < 0:
            spin = max(spin, -self.max_english)
        else:
            spin = min(spin, self.max_english)
        vx = self.vx
        vy = self.vy
        r = sqrt(vx * vx + vy * vy)
        theta = atan2(vy, vx) + spin
        self.vx = r * cos(theta)
        self.vy = r * sin(theta)

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


class CountdownAnimation:
    def __init__(self):
        self.value = 0
        self.speed = 4

    def update(self, delta_t):
        self.value += delta_t * self.speed

    def draw(self, display):
        width, height = display.size
        x = width // 2

        set_pixel = display.set_pixel
        value = int(self.value)
        if value == 0:
            lit = -1
        else:
            lit = (value - 1) % height
        for y in range(height):
            if y & 1:
                continue
            set_pixel(x, y, 255 if y == lit else 64 if lit & 1 else 128)


class ScoreAnimation:
    BITMAP = b'""*>\x14\x00\x1c\x08\x08\x08\x1c\x00"2*&"'

    def __init__(self, rotate_180=False):
        self.rotate_180 = rotate_180
        self.offsets = (0, 1, 2)
        self.period = 0.09
        self.time = 0
        self.update(0)

    def update(self, delta_t):
        time = self.time + delta_t
        self.time = time
        nperiods = int(time / self.period)
        offsets = self.offsets
        self.offset = offsets[nperiods % len(offsets)]

    def draw(self, display):
        width, height = display.size

        if (rotate := self.rotate_180):
            yrange = range(height - 1, -1, -1)
        else:
            yrange = range(height)

        offset = self.offset
        set_pixel = display.set_pixel
        for x, bits in enumerate(self.BITMAP):
            bx = width - x + offset
            if rotate:
                x = width - 1 - x
            mask = 1
            for y in yrange:
                bit_set = bits & mask
                mask <<= 1
                if not bit_set:
                    continue
                v = 192 if ((bx - abs(y - 3)) & 2) else 160
                set_pixel(x, y, v)


def main(*args, **kwargs):
    Game(*args, **kwargs).run()


if __name__ == "__main__":
    main()
