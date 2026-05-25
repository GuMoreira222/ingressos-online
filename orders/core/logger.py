import sys
import logging


try:
    from loguru import logger

    logger.remove()
    logger.add(
        sys.stdout,
        format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {module}:{function}:{line} - {message}",
        level="INFO",
        serialize=True,
    )
except ModuleNotFoundError:
    logger = logging.getLogger("orders")
    logging.basicConfig(stream=sys.stdout, level=logging.INFO)


def get_logger():
    return logger
