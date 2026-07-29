import logging

from server.app.cli import parse_args
from server.app.modes import run_main_mode, run_test_mode
from server.app.logging import setup_logging

logger = logging.getLogger(__name__)


def main() -> None:
    args = parse_args()
    setup_logging(args.debug)
    try:
        {"main": run_main_mode, "test": run_test_mode}[args.mode](args)
    except ValueError as error:
        logger.error("%s", error)
        raise SystemExit(1) from error
