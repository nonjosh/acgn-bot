"""Utility functions"""
from datetime import datetime


def print_t(msg: str):
    """print with timestamp

    Args:
        msg (str): message string
    """
    now = datetime.now()
    current_time = now.strftime("%Y/%m/%d %H:%M:%S")
    print(f"[{current_time}] {msg}")


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
