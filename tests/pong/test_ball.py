import math
import random

from itertools import product
from unittest.mock import Mock, NonCallableMock, patch

import pytest

from target.pong import Ball, Game


# 0 X 0.5
# 1 |
# 2 |
# 3 X
# 4 |
# 5 |
# 6 X 6.5

@pytest.mark.parametrize(
    "start_pos,delta,expect_pos", (
        # non-bounces
        ((8, 3), (2, 2), (10, 5)),
        ((8, 3), (2, -1), (10, 2)),
        ((8, 3), (-3, -2), (5, 1)),
        ((8, 3), (-2, 2.5), (6, 5.5)),
        # single bounces
        ((2, 1), (3, -3), (5, 3)),  # top edge
        ((2, 5), (3, 3), (5, 5)),  # bottom edge
        ((3, 6), (2, 2), (5, 5)),  # same
        # bounce off left paddle,
        # which is at x=1.5:
        # - start at (3, 2)
        # - hit at (1.5, 3)
        # - end up at (3, 4)
        ((3, 2), (-3, 2), (3, 4)),
        # bounce off right paddle,
        # which is at x=15.5:
        # - start at (14, 2)
        # - hit at (15.5, 3)
        # - end up at (14, 4)
        ((14, 2), (3, 2), (14, 4)),
    ))
def test_bounce(start_pos, delta, expect_pos):
    game = Game(NonCallableMock())

    ball = game.ball
    ball.x, ball.y = start_pos
    ball.vx, ball.vy = delta

    ball.update(1, game.players)

    assert (ball.x, ball.y) == pytest.approx(expect_pos)


@patch("target.engine._PicoScroll")
def test_no_draw_offscreen(picoscroll_cls: Mock):
    pixels_set = 0

    def _set_pixel(x, y, v):
        nonlocal pixels_set
        pixels_set += 1

        assert isinstance(x, int)
        assert isinstance(y, int)
        assert isinstance(v, int)
        assert 0 <= x < 17
        assert 0 <= y < 7
        assert 0 <= v < 256

    picoscroll = NonCallableMock()
    picoscroll.set_pixel = _set_pixel

    picoscroll_cls.return_value = picoscroll

    game = Game()
    picoscroll_cls.assert_called_once_with()
    paddle_pixels = 6  # 3 for each paddle
    assert pixels_set == paddle_pixels

    game.draw_ball = True

    values = [
        0, 0.1, 1, 1.1, 2, 2.1, math.e, math.pi, 5, 5.1,
        6, 6.1, 7, 7.1, 15, 15.1, 16, 16.1, 20, 40, 1e6,
    ]

    values = [v - 0.5 for v in values] + values + [v + 0.5 for v in values]
    values = list(sorted(set([-v for v in values] + values)))
    values = list(product(values, values))

    hist = [0] * 5

    for shuffle in (False, True):
        if shuffle:
            expect_hist = [v * 2 for v in hist]
            random.shuffle(values)
        for xy in values:
            pixels_set = 0
            game.ball.x, game.ball.y = xy
            game._draw()
            pixels_set -= paddle_pixels
            assert 0 <= pixels_set <= 4
            hist[pixels_set] += 1
        print(hist)
    assert hist == expect_hist
    assert hist[3] == 0
    assert hist == [19538, 160, 1200, 0, 2000]


@pytest.mark.parametrize(
    "ball_xy,expect_set_pixels", (
        ((2.5, 4.5),
         ((2, 4, 255), (3, 4, 0),
          (2, 5,   0), (3, 5, 0),
          )),
        ((2.25, 4.5),
         ((1, 4, 64), (2, 4, 191),
          (1, 5,  0), (2, 5,   0),
          )),
        ((2.5, 4.75),
         ((2, 4, 191), (3, 4, 0),
          (2, 5,  64), (3, 5, 0),
          )),
        ((3, 5),
         ((2, 4, 64), (3, 4, 64),
          (2, 5, 64), (3, 5, 64),
          )),
    ))
def test_antialiasing(ball_xy, expect_set_pixels):
    ball = Ball()

    ball.x, ball.y = ball_xy

    set_pixel = Mock()
    ball.draw(set_pixel)

    assert set_pixel.call_count == 4
    calls = set_pixel.call_args_list
    assert not any(call.kwargs for call in calls)
    calls = [list(call.args) for call in calls]
    for actual, expect in zip(calls, expect_set_pixels):
        actual[2] = round(actual[2])
        actual = tuple(actual)
        assert actual == expect
