import logging


def setup_logging(debug: bool):
    level = logging.DEBUG if debug else logging.INFO

    if debug:
        log_format = "[%(levelname)s] (%(filename)s:%(funcName)s) %(message)s"
    else:
        log_format = "[%(levelname)s] %(message)s"

    logging.basicConfig(level=level, format=log_format)
