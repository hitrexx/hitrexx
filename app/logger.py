import logging
import os

REQUESTS_LOGGER_NAME = "ai_estimate.requests"
ERRORS_LOGGER_NAME = "ai_estimate.errors"

_LOG_FORMAT = "%(asctime)s | %(levelname)s | %(name)s | %(message)s"


def setup_logging(log_level: str = "INFO", logs_dir: str = "logs") -> None:
    os.makedirs(logs_dir, exist_ok=True)
    formatter = logging.Formatter(_LOG_FORMAT)

    root = logging.getLogger()
    root.setLevel(log_level)
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    root.addHandler(console_handler)

    requests_handler = logging.FileHandler(os.path.join(logs_dir, "requests.log"), encoding="utf-8")
    requests_handler.setFormatter(formatter)
    requests_logger = logging.getLogger(REQUESTS_LOGGER_NAME)
    requests_logger.setLevel(logging.INFO)
    requests_logger.addHandler(requests_handler)
    requests_logger.propagate = False

    errors_handler = logging.FileHandler(os.path.join(logs_dir, "errors.log"), encoding="utf-8")
    errors_handler.setFormatter(formatter)
    errors_logger = logging.getLogger(ERRORS_LOGGER_NAME)
    errors_logger.setLevel(logging.ERROR)
    errors_logger.addHandler(errors_handler)
    errors_logger.propagate = False


def get_requests_logger() -> logging.Logger:
    return logging.getLogger(REQUESTS_LOGGER_NAME)


def get_errors_logger() -> logging.Logger:
    return logging.getLogger(ERRORS_LOGGER_NAME)
