from unittest.mock import NonCallableMock

import pytest

from target.pong import Game


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

    assert (ball.x, ball.y) == expect_pos
