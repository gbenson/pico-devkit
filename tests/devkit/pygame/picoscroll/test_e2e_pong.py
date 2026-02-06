import logging

from dataclasses import dataclass
from collections.abc import Iterable
from itertools import cycle, product
from time import time
from typing import Optional
from unittest.mock import Mock, NonCallableMock

import pytest

from pygame import K_a, K_b, K_x, K_y, K_s, KEYUP, KEYDOWN

from target.pong import Game, main

logger = logging.getLogger(__name__)
d = logger.info


# Tests

def test_pong_e2e(pygame: Mock, monkeypatch: pytest.MonkeyPatch) -> None:
    key_sequence = cycle(
        NonCallableMock(type=type, key=key)
        for key, type in product(
                (K_a, K_b, K_x, K_y, K_s),
                (KEYDOWN, KEYUP),
        )
    )

    last_key = time()
    def keysmasher() -> Iterable[Mock]:
        nonlocal last_key
        if time() - last_key < 0.02:
            return []
        last_key = time()
        return [next(key_sequence)]

    deadliner = Deadliner(timeout=1)

    pygame.event.get = keysmasher
    pygame.display.flip = deadliner

    assert len(pygame.mock_calls) == 0  # sanity

    monkeypatch.setattr(Game, "DEBOUNCE", 0)
    try:
        start_time = time()
        with pytest.raises(DeadlineExceeded):
            main()
    finally:
        d(f"ran for {time() - start_time:.2f}s")
        d(f"len(pygame.mock_calls) = {len(pygame.mock_calls)}")
        for i, call in enumerate(pygame.mock_calls[:20]):
            d(f"call {i+1}: {call}")

    assert len(pygame.mock_calls) == 5

    pygame.init.assert_called_once_with()
    pygame.display.set_mode.assert_called_once_with((629, 259))
    pygame.display.set_caption.called_once_with("Pico Scroll")

    num_frames = deadliner.num_calls
    d(f"num_frames={num_frames}")
    assert 55 < num_frames < 65  # it targets 60fps


# Helpers

@dataclass
class Deadliner:
    timeout: Optional[float] = None
    deadline: Optional[float] = None
    num_calls: int = 0

    def __call__(self) -> None:
        self.num_calls += 1
        if self.deadline is not None:
            if time() > self.deadline:
                raise DeadlineExceeded
        elif self.timeout is not None:
            self.deadline = time() + self.timeout


class DeadlineExceeded(TimeoutError):
    pass
