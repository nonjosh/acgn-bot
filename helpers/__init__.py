"""helpers for web scrapping"""
import logging
from typing import List
from abc import ABC, abstractmethod
from urllib.parse import urlparse
from helpers import checkers


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


class AbstractChapterHelper(ABC):
    """Abstract helper class"""

    def __init__(self, name: str, urls: List, logger_name="dev") -> None:
        self.logger = logging.getLogger(logger_name)

        self.name = name
        self.urls = urls

        # Only check first url
        self.check_url = urls[0]
        self.main_domain_name = get_main_domain_name(self.check_url)
        self.checker = None
        self.media_type = None

        # Set checker and media_type
        self.set_checker()

    @abstractmethod
    def set_checker(self) -> None:
        """set checker and media_type"""
        raise NotImplementedError


class NovelChapterHelper(AbstractChapterHelper):
    """Novel helper class"""

    def set_checker(self) -> None:
        """Initialize checker"""

        checker_dict = {
            "wutuxs": checkers.WutuxsChecker(check_url=self.check_url),
            "syosetu": checkers.SyosetuChecker(check_url=self.check_url),
            "99wx": checkers.WxChecker(check_url=self.check_url),
        }
        # Check if domain name is in checker_dict
        if self.main_domain_name in checker_dict:
            self.checker = checker_dict[self.main_domain_name]
            self.media_type = "novel"
        else:
            raise ValueError(
                f"Website {self.main_domain_name} is not supported yet."
            )


class ComicChapterHelper(AbstractChapterHelper):
    """Comic helper class"""

    def set_checker(self) -> None:
        """Initialize checker"""

        checker_dict = {
            "manhuagui": checkers.ManhuaguiChecker(check_url=self.check_url),
            "qiman57": checkers.QimanChecker(check_url=self.check_url),
            "baozimh": checkers.BaozimhChecker(check_url=self.check_url),
            "xbiquge": checkers.XbiqugeChecker(check_url=self.check_url),
        }
        # Check if domain name is in checker_dict
        if self.main_domain_name in checker_dict:
            self.checker = checker_dict[self.main_domain_name]
            self.media_type = "comic"
        else:
            raise ValueError(
                f"Website {self.main_domain_name} is not supported yet."
            )
