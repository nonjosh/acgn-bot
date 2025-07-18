import threading
import time
from typing import List
from urllib.parse import urlparse, urlunparse

from bs4.element import Tag

from helpers.chapter import Chapter
from helpers.checkers.base import AbstractChapterChecker
from helpers.utils import get_logger


class ManhuaguiChecker(AbstractChapterChecker):
    """Manhuagui chapter list"""

    URL_SUBSTRING = "manhuagui"

    # Class-level rate limiting variables
    _last_request_time = 0
    _min_request_interval = 30  # 30 seconds minimum between requests
    _request_lock = None
    _logger = get_logger(__name__)

    def __init__(self, check_url: str) -> None:
        """Initialize ManhuaguiChecker with rate limiting"""
        super().__init__(check_url)
        # Import threading here to avoid circular imports
        if ManhuaguiChecker._request_lock is None:
            ManhuaguiChecker._request_lock = threading.Lock()

        # Set more conservative request parameters for manhuagui
        self.retry_interval = 10  # Increase retry interval to 10 seconds
        self.max_retry_num = 2  # Reduce max retries to avoid too many attempts

    def _wait_for_rate_limit(self) -> None:
        """Enforce rate limiting by waiting if necessary"""
        with ManhuaguiChecker._request_lock:
            current_time = time.time()
            time_since_last_request = current_time - ManhuaguiChecker._last_request_time

            if time_since_last_request < ManhuaguiChecker._min_request_interval:
                wait_time = (
                    ManhuaguiChecker._min_request_interval - time_since_last_request
                )
                ManhuaguiChecker._logger.info(
                    "Rate limiting for manhuagui: waiting %.1f seconds before next request",
                    wait_time,
                )
                time.sleep(wait_time)

            ManhuaguiChecker._last_request_time = time.time()

    def get_latest_response(self, url: str = None, apparent_encoding: bool = True):
        """Override to add rate limiting before making requests"""
        self._wait_for_rate_limit()
        return super().get_latest_response(url, apparent_encoding)

    def get_latest_post_response(
        self, url: str = None, data: dict = None, apparent_encoding: bool = True
    ):
        """Override to add rate limiting before making POST requests"""
        self._wait_for_rate_limit()
        return super().get_latest_post_response(url, data, apparent_encoding)

    @classmethod
    def set_rate_limit_interval(cls, interval_seconds: int) -> None:
        """Set the minimum interval between requests

        Args:
            interval_seconds (int): Minimum seconds between requests
        """
        if interval_seconds > 0:
            cls._min_request_interval = interval_seconds
            cls._logger.info(
                "Manhuagui rate limit interval set to %d seconds", interval_seconds
            )
        else:
            cls._logger.warning(
                "Invalid rate limit interval: %d. Must be positive.", interval_seconds
            )

    def get_latest_chapter_list(self) -> List[Chapter]:
        """Get latest chapter list from manhuagui

        Returns:
            List[Chapter]: latest chapter list
        """
        soup = self.get_latest_soup()
        if not soup:
            return []

        comic_path = urlparse(self.check_url).path

        a_tags = soup.findAll("a")

        chapter_list = []
        for i in range(0, len(a_tags) - 1):  # 'a' tags are for links
            one_a_tag: Tag = a_tags[i]

            try:
                chapter_path = one_a_tag["href"]
                if chapter_path.startswith(comic_path):
                    chapter_title = one_a_tag.text
                    chapter_url = urlunparse(
                        urlparse(self.check_url)._replace(path=chapter_path)
                    )
                    chapter_list.append(Chapter(title=chapter_title, url=chapter_url))
            except KeyError:
                pass

        return chapter_list[::-1]
