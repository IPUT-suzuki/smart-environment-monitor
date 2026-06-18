from modes.mock import run_mock_mode
from modes.test import run_test_mode
from modes.main import run_main_mode

MODE_HANDLERS = {
    "main": run_main_mode,
    "mock": run_mock_mode,
    "test": run_test_mode,
}


def run_mode(args):
    handler = MODE_HANDLERS.get(args.mode)
    if handler is None:
        raise ValueError(f"unknown mode: {args.mode}")
    handler(args)
