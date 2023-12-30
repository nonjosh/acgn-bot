from abc import ABC, abstractmethod
from typing import List
import time
import json
import requests
from bs4 import BeautifulSoup
from helpers.chapter import Chapter
from helpers.utils import DEFAULT_HEADERS, DEFAULT_REQUEST_TIMEOUT, get_list_diff


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
        self.headers = DEFAULT_HEADERS
        self.retry_interval = 5
        self.max_retry_num = 3
        self.chapter_list = []
        self.updated_chapter_list = []

        self.last_check_time = None

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

        request_sucess = False
        retry_num = 0

        while not request_sucess:
            try:
                # Send with GET method
                response = requests.get(
                    url=url,
                    params=self.params,
                    headers=self.headers,
                    timeout=self.request_timeout,
                )
                if response.status_code == 200:
                    # override encoding by real educated guess as provided by chardet
                    if apparent_encoding:
                        response.encoding = response.apparent_encoding
                    request_sucess = True
                else:
                    time.sleep(self.retry_interval)

                # Check if response headers contains set-cookie PHPSESSID
                # If yes, set the cookie to the request header for the next request
                #
                # now syosetu and mn4u both have `set-cookie` in response headers,
                # but only mn4u have the string `PHPSESSID=` on first visit
                if (
                    "set-cookie" in response.headers
                    and "PHPSESSID=" in response.headers["set-cookie"]
                ):
                    self.headers["Cookie"] = response.headers["set-cookie"]
                    request_sucess = False
                    print("Set cookie to request header")
            except requests.exceptions.ConnectionError:
                return None
            except requests.exceptions.RequestException:
                time.sleep(self.retry_interval)
            retry_num += 1

            # break and return empty response if reach MAX_RETRY_NUM
            if retry_num >= self.max_retry_num:
                return None

        return response

    def get_lastest_post_response(
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

        request_sucess = False
        retry_num = 0

        while not request_sucess:
            try:
                # Send with POST method
                response = requests.post(
                    url=url,
                    data=data,
                    headers=self.headers,
                    timeout=self.request_timeout,
                )
                if response.status_code == 200:
                    # override encoding by real educated guess as provided by chardet
                    if apparent_encoding:
                        response.encoding = response.apparent_encoding
                    request_sucess = True
                else:
                    time.sleep(self.retry_interval)
            except json.decoder.JSONDecodeError:
                time.sleep(self.retry_interval)
            except requests.exceptions.ConnectionError:
                return []
            except requests.exceptions.RequestException:
                time.sleep(self.retry_interval)
            retry_num += 1

            # break and return empty response if reach MAX_RETRY_NUM
            if retry_num >= self.max_retry_num:
                return None
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

    def get_updated_chapter_list(self) -> List[Chapter]:
        """Get list of updated chapter objects

        Returns:
            List[Chapter]: list of Chapter objects
        """
        self.updated_chapter_list = []

        # Get latest chapter list
        latest_chapter_list = self.get_latest_chapter_list()

        # Get list of updated chapters if new chapter list is valid (not empty)
        if len(latest_chapter_list) > 0:
            self.updated_chapter_list = get_list_diff(
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
