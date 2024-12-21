"""Utility functions"""

import logging
from datetime import datetime
from logging.handlers import TimedRotatingFileHandler
from typing import List
from urllib.parse import urlparse

import requests

from helpers.chapter import Chapter

# Create logging formatter
FORMATTER = logging.Formatter(
    "[%(asctime)s] {%(pathname)s:%(lineno)d} %(levelname)s - %(message)s",
    "%Y-%m-%dT%H:%M:%S%z",
)

LOG_FILE = "./logs/app.log"

DEFAULT_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5)"
        " AppleWebKit/537.36 (KHTML, like Gecko)"
        " Chrome/50.0.2661.102 Safari/537.36"
    )
}

DEFAULT_REQUEST_TIMEOUT = 5


def get_logger(logger_name: str, log_level: int = logging.INFO) -> logging.Logger:
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
    e.g. "https://ncode.syosetu.com/n6621fl"-> "syosetu"

    Args:
        url_str (str): url string

    Returns:
        str: domain name of url
    """
    netloc = urlparse(url_str).netloc
    main_domain_name = netloc.split(".")[-2]

    return main_domain_name


def check_url_valid(url: str, request: bool = True, verbose: bool = False) -> bool:
    """Check if url is valid

    Args:
        url (str): url string
        verbose (bool, optional): verbose. Defaults to False.

    Returns:
        bool: True if valid, False if not
    """
    # Check format
    try:
        result = urlparse(url)
        if not all([result.scheme, result.netloc, result.path]):
            return False
    except ValueError:
        return False

    if not request:
        return True

    # Check by requests
    try:
        response = requests.get(
            url, headers=DEFAULT_HEADERS, timeout=DEFAULT_REQUEST_TIMEOUT
        )
        if response.status_code != 200:
            return False
        # Handle redirect
        if response.url != url:
            return False
    except requests.exceptions.HTTPError as errh:
        if verbose:
            print("Http Error:", errh)
    except requests.exceptions.ConnectionError as errc:
        if verbose:
            print("Error Connecting:", errc)
    except requests.exceptions.Timeout as errt:
        if verbose:
            print("Timeout Error:", errt)
    except requests.exceptions.RequestException as err:
        if verbose:
            print("OOps: Something Else", err)
    else:
        return True
    return False


def get_chapter_list_diff(
    new_list: List[Chapter], old_list: List[Chapter]
) -> List[Chapter]:
    """Get list of items that not in old list

    Args:
        new_list (List[Chapter]): new list
        old_list (List[Chapter]): old list

    Returns:
        List[Chapter]: list of items that not in old list
    """
    old_urls = {item.url for item in old_list}
    diff_list = [item for item in new_list if item.url not in old_urls]
    return diff_list
