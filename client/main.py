from cli import parse_args
from logger import setup_logging
from modes.registry import run_mode


def main():
    args = parse_args()
    setup_logging(args.debug)
    run_mode(args)


if __name__ == "__main__":
    main()
