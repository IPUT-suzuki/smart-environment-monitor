import json
import logging
from typing import Any


def setup_logging(debug: bool) -> None:
    level = logging.DEBUG if debug else logging.INFO
    log_format = "[%(levelname)s] (%(filename)s:%(funcName)s) %(message)s" if debug else "[%(levelname)s] %(message)s"
    logging.basicConfig(level=level, format=log_format)


def log_debug_data(logger: logging.Logger, event: str, data: Any) -> None:
    """Log structured debug data on multiple indented lines."""
    if not logger.isEnabledFor(logging.DEBUG):
        return
    formatted = json.dumps(data, ensure_ascii=False, indent=2, default=str)
    logger.debug("%s:\n%s", event, formatted)
