import json
import time
from abc import ABC, abstractmethod
from typing import List

import backoff
import requests
from bs4 import BeautifulSoup

from helpers.chapter import Chapter
from helpers.utils import (
    DEFAULT_HEADERS,
    DEFAULT_REQUEST_TIMEOUT,
    get_chapter_list_diff,
    get_logger,
)

logger = get_logger(__name__)

CHECKER_FETCH_EXCEPTIONS = (
    requests.exceptions.RequestException,
    json.decoder.JSONDecodeError,
    AttributeError,
    KeyError,
    IndexError,
    TypeError,
    ValueError,
)


class AbstractChapterChecker(ABC):
    """Abstract checker class"""

    URL_SUBSTRING: str = ""

    def __init__(
        self,
        check_url: str,
    ) -> None:
        self.check_url = check_url
        self.params = {}
        self.request_timeout = DEFAULT_REQUEST_TIMEOUT
        self.headers = DEFAULT_HEADERS.copy()
        self.proxies: dict = {}
        self.retry_interval = 5
        self.max_retry_num = 3
        self.chapter_list = []
        self.updated_chapter_list = []
        # True once a fetch succeeded but returned zero chapters: the producer
        # (e.g. a bilibili uploader) had no episode when the checker was added,
        # so the first episode to appear later is news, not restart backfill
        self.observed_empty = False

        self.last_check_time = None

    @backoff.on_exception(
        backoff.expo,
        (requests.exceptions.RequestException, json.decoder.JSONDecodeError),
        max_tries=3,
        jitter=backoff.full_jitter,
    )
    def get_latest_response(
        self, url: str = None, apparent_encoding: bool = True
    ) -> requests.Response:
        """Get latest response

        Args:
            url (str): url (Default: {self.check_url})
            apparent_encoding (bool): whether to use apparent encoding

        Returns:
            requests.Response: latest response
        """
        # Update last check time
        self.last_check_time = time.strftime("%Y-%m-%dT%H:%M:%S%z")

        # Get url
        if url is None:
            url = self.check_url

        # Send with GET method
        # Let ConnectionError/Timeout propagate: backoff retries transient
        # network failures (flaky proxy etc.) and they are dropped only when a
        # declared-maxima-level caller decides what a failed fetch means.
        response = requests.get(
            url=url,
            params=self.params,
            headers=self.headers,
            timeout=self.request_timeout,
            proxies=self.proxies or None,
        )
        if response.status_code == 200:
            # override encoding by real educated guess as provided by chardet
            if apparent_encoding:
                response.encoding = response.apparent_encoding
        else:
            raise requests.exceptions.RequestException(
                f"Unexpected status code: {response.status_code}"
            )

        # Check if response headers contains set-cookie PHPSESSID
        # If yes, set the cookie to the request header for the next request
        #
        # now syosetu and mn4u both have `set-cookie` in response headers,
        # but only mn4u have the string `PHPSESSID=` on first visit
        if "set-cookie" in response.headers and "PHPSESSID=" in response.headers["set-cookie"]:
            self.headers["Cookie"] = response.headers["set-cookie"]

        return response

    @backoff.on_exception(
        backoff.expo,
        (requests.exceptions.RequestException, json.decoder.JSONDecodeError),
        max_tries=3,
        jitter=backoff.full_jitter,
    )
    def get_latest_post_response(
        self,
        url: str = None,
        data: dict = None,
        apparent_encoding: bool = True,
    ) -> requests.Response:
        """Get latest response with POST method

        Args:
            url (str): url (Default: {self.check_url})
            apparent_encoding (bool): whether to use apparent encoding

        Returns:
            requests.Response: latest response
        """
        # Update last check time
        self.last_check_time = time.strftime("%Y-%m-%dT%H:%M:%S%z")

        # Get url
        if url is None:
            url = self.check_url

        # Send with POST method
        # Like get_latest_response above, transient network failures propagate
        # to the backoff decorator instead of being swallowed into a fake
        # empty result.
        response = requests.post(
            url=url,
            data=data,
            headers=self.headers,
            timeout=self.request_timeout,
            proxies=self.proxies or None,
        )
        if response.status_code == 200:
            # override encoding by real educated guess as provided by chardet
            if apparent_encoding:
                response.encoding = response.apparent_encoding
        else:
            raise requests.exceptions.RequestException(
                f"Unexpected status code: {response.status_code}"
            )

        return response

    def get_latest_soup(self, apparent_encoding: bool = True) -> BeautifulSoup:
        """Get latest soup

        Args:
            apparent_encoding (bool): whether to use apparent encoding

        Returns:
            BeautifulSoup: latest soup
        """
        response = self.get_latest_response(apparent_encoding=apparent_encoding)
        if response is None:
            return None
        return BeautifulSoup(response.text, "html.parser")

    def get_updated_chapter_list(self) -> List[Chapter] | None:
        """Get list of updated chapter objects

        Returns:
            List[Chapter]: list of Chapter objects,
            or None when the fetch failed (chapter_list left untouched)
        """
        self.updated_chapter_list = []

        # Get latest chapter list
        try:
            latest_chapter_list = self.get_latest_chapter_list()
        except CHECKER_FETCH_EXCEPTIONS as err:
            logger.exception(
                "Checker failed for url %s: %s",
                self.check_url,
                err,
            )
            return None

        # Get list of updated chapters if new chapter list is valid (not empty)
        if len(latest_chapter_list) > 0:
            self.updated_chapter_list = get_chapter_list_diff(
                latest_chapter_list, self.chapter_list
            )
            # Update chapter list
            self.chapter_list = latest_chapter_list

            # Return updated chapter list
            return self.updated_chapter_list
        return []

    @abstractmethod
    def get_latest_chapter_list(self) -> List[Chapter]:
        """Get latest chapter list

        Returns:
            List[Chapter]: latest chapter list
        """
        raise NotImplementedError

    def get_latest_chapter(self) -> Chapter:
        """Get latest chapter

        Returns:
            Chapter: latest chapter
        """
        if len(self.chapter_list) > 0:
            return self.chapter_list[-1]
        return None
