import logging

from colorama import Fore

LOGGER_NAME: str = "tiny-web-crawler"
DEFAULT_LOG_LEVEL: int = logging.INFO


class ColorFormatter(logging.Formatter):
    message_format: str = "%(levelname)s %(message)s"

    FORMATS = {
        logging.DEBUG: Fore.LIGHTBLUE_EX + message_format + Fore.RESET,
        logging.INFO: Fore.BLUE + message_format + Fore.RESET,
        logging.WARNING: Fore.YELLOW + message_format + Fore.RESET,
        logging.ERROR: Fore.RED + message_format + Fore.RESET,
        logging.CRITICAL: Fore.RED + message_format + Fore.RESET,
    }

    def format(self, record: logging.LogRecord) -> str:
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)


def get_logger() -> logging.Logger:
    return logging.getLogger(LOGGER_NAME)


def set_logging_level(level: int) -> None:
    get_logger().setLevel(level=level)


get_logger().setLevel(level=DEFAULT_LOG_LEVEL)

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)

console_handler.setFormatter(ColorFormatter())

get_logger().addHandler(console_handler)
