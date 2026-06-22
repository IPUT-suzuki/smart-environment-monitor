from app.cli import parse_args
from app.modes import run_main_mode, run_mock_mode, run_test_mode
from app.logging import setup_logging

MODE_HANDLERS = {"main": run_main_mode, "mock": run_mock_mode, "test": run_test_mode}


def main() -> None:
    args = parse_args()
    setup_logging(args.debug)
    MODE_HANDLERS[args.mode](args)
