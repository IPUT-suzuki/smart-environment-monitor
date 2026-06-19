import logging

from cli import parse_args
from modes.registry import run_mode
from utils.logger import setup_logging

logger = logging.getLogger(__name__)


def main():
    args = parse_args()
    setup_logging(args.debug)

    try:
        run_mode(args)
    except ValueError as e:
        logger.error(e)
        exit(1)


if __name__ == "__main__":
    main()
