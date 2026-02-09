from math import pi as PI
from typing import Any
from time import sleep
from unittest.mock import Mock, patch

import pytest

from pytest import approx

from engine import RateLimiter


def test_init_defaults():
    c = RateLimiter()
    assert c.max_rate is None
    assert c.min_interval == 0
    assert c.min_interval_us == 0


def test_init_with_limit():
    c = RateLimiter(23 * PI)
    assert c.max_rate == approx(72.2566)
    assert c.min_interval == approx(0.01383956)
    assert c.min_interval_us == approx(13839.56)


def test_setters():
    c = RateLimiter(60)

    c.min_interval_us += 1
    assert c.min_interval_us == approx(16667.67)
    assert c.min_interval_us != approx(1e6/60)
    assert c.min_interval == approx(0.01666767)
    assert c.max_rate == approx(59.9964)
    assert c.max_rate != approx(60)

    c.min_interval *= 1.125
    assert c.min_interval == approx(0.01875112)
    assert c.min_interval != approx(0.01666767)
    assert c.min_interval_us == approx(18751.12)
    assert c.max_rate == approx(53.3301)


@patch("target.engine.sleep_us")
@pytest.mark.parametrize(
    "attr",
    ("max_rate", "min_interval", "min_interval_us"),
)
@pytest.mark.parametrize(
    "value",
    (0, -1, -1.0, 0.0, None, False),
)
def test_clear_max_rate(sleep_us: Mock, attr: str, value: Any):
    c = RateLimiter(50)
    setattr(c, attr, value)

    assert c.max_rate is None
    assert c.min_interval == 0
    assert c.min_interval_us == 0
    assert c._min_interval_us == 0

    c.wait_us()
    c.wait_us()
    sleep_us.assert_not_called()


@patch("target.engine.sleep_us")
def test_no_unnecessary_sleeping(sleep_us: Mock):
    c = RateLimiter()
    c.min_interval_us = 1
    assert c.max_rate == approx(1_000_000)

    c.wait_us()
    sleep_us.assert_not_called()
    sleep(1e-3)
    c.wait_us()
    sleep_us.assert_not_called()
