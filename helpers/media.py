"""Media Helper class"""

import logging
from typing import List, Literal
from helpers.checkers import get_checker_for_url
from helpers.checkers.base import AbstractChapterChecker
from helpers.utils import get_main_domain_name, check_url_valid


MediaTypes = Literal["novel", "comic"]


class MediaHelper:
    """Abstract helper class"""

    def __init__(
        self,
        name: str,
        urls: List,
        media_type: MediaTypes,
        logger_name="dev",
    ) -> None:
        self.logger = logging.getLogger(logger_name)

        self.name = name
        self.urls = urls
        self.media_type = media_type
        assert self.media_type in ["novel", "comic"]

        self.checker: AbstractChapterChecker = None

        # Set check_url, main_domain_name and checker
        # Check if first url is valid, if not, use the next one
        for url in self.urls:
            if check_url_valid(url):
                self.check_url = url
                self.main_domain_name = get_main_domain_name(self.check_url)
                # Set checker
                if self.set_checker():
                    # Escape for loop if checker is set successfully
                    break
        else:
            # Use the first url if all urls are invalid
            self.check_url = self.urls[0]

    def set_checker(self) -> bool:
        """Initialize checker by checking keyword in check_url

        Returns:
            bool: True if checker is set successfully
        """

        # Check if domain name is in checker_dict
        self.checker = get_checker_for_url(self.check_url)
        if self.checker:
            self.logger.info("Checker %s is set for %s", self.checker, self.check_url)
            return True
        self.logger.info("No checker is set for %s", self.check_url)
        return False

    def get_urls_text(self) -> str:
        """Construct urls text from urls
            e.g. qiman59 | cocomanga

        Returns:
            str: urls text
        """
        urls_texts = [
            f"<a href='{url}'>{get_main_domain_name(url)}</a>" for url in self.urls
        ]
        return " | ".join(urls_texts) + "\n"
