import logging
from logging import DEBUG, INFO, WARNING, ERROR, CRITICAL, FATAL, NOTSET # pylint: disable=unused-import

LOGGER_NAME: str = "tiny-web-crawler-logger"
DEFAULT_LOG_LEVEL = INFO

logging.basicConfig(level=DEFAULT_LOG_LEVEL)

def get_logger() -> logging.Logger:
    return logging.getLogger(LOGGER_NAME)

def set_logging_level(level:int) -> None:
    get_logger().setLevel(level=level)
