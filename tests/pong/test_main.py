from unittest.mock import Mock, NonCallableMock, patch

from target.pong import main


@patch("target.pong.PicoScroll")
@patch("target.pong.Game.run")
def test_default(game_run: Mock, picoscroll_init: Mock) -> None:
    main()
    picoscroll_init.assert_called_once_with()
    game_run.assert_called_once()


@patch("target.pong.PicoScroll")
@patch("target.pong.Game.run")
def test_with_display(game_run: Mock, picoscroll_init: Mock) -> None:
    main(NonCallableMock())
    picoscroll_init.assert_not_called()
    game_run.assert_called_once()
