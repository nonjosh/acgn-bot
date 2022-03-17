"""Utility functions"""
from datetime import datetime
import logging
from logging.handlers import TimedRotatingFileHandler

# Create logging formatter
FORMATTER = logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    "%Y-%m-%dT%H:%M:%S%z",
)

LOG_FILE = "./logs/app.log"


def get_logger(
    logger_name: str, log_level: int = logging.INFO
) -> logging.Logger:
    """Set logger

    Args:
        log_file (str): log file path
        log_level (int, optional): log level. Defaults to logging.INFO.

    return:
        logging.Logger: logger object
    """
    logger = logging.getLogger(logger_name)
    logger.setLevel(log_level)

    # Create console handler and set level to debug
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)

    # Add formatter to console_handler
    console_handler.setFormatter(FORMATTER)

    # Add console_handler to logger
    logger.addHandler(console_handler)

    # Create error file handler and set level to error
    file_handler = TimedRotatingFileHandler(filename=LOG_FILE, when="midnight")
    file_handler.setLevel(log_level)

    # Add formatter to file_handler
    file_handler.setFormatter(FORMATTER)

    # Add file_handler to logger
    logger.addHandler(file_handler)

    return logger


def within_check_period(start_hour: str, end_hour: str) -> bool:
    """Check if within check period

    Args:
        start_hour (str): start hour (e.g. "08")
        end_hour (str): end hour (e.g. "20")

    Returns:
        bool: True if within check period, False if not
    """
    now = datetime.now()
    current_hour = now.strftime("%H")

    return start_hour <= int(current_hour) <= end_hour


def get_main_domain_name(url_str) -> str:
    """get url domain texts

    Args:
        url_str (str): url string

    Returns:
        str: domain name of url
    """
    domain_name = url_str.split("/")[2]
    main_domain_name = domain_name.split(".")[-2]

    return main_domain_name
