"""Checkers"""
from abc import ABC, abstractmethod
from typing import List
import time
from urllib.parse import urlparse, urlunparse
import requests
from bs4 import BeautifulSoup
from helpers.chapter import Chapter


def get_chapter_list_diff(new_list: List, old_list: List) -> List[Chapter]:
    """Get list of new chapters that not in old list

    Args:
        new_list (List[Chapter]): new chapter list
        old_list (List[Chapter]): old chapter list

    Returns:
        List[Chapter]: list of new chapters that not in old list
    """
    diff_list = []
    for new_chp in new_list:
        if new_chp not in old_list:
            diff_list.append(new_chp)
    return diff_list


class AbstractChapterChecker(ABC):
    """Abstract checker class"""

    def __init__(
        self, check_url: str, retry_interval: int = 5, max_retry_num: int = 3
    ) -> None:
        self.check_url = check_url
        self.retry_interval = retry_interval
        self.max_retry_num = max_retry_num
        self.chapter_list = []
        self.updated_chapter_list = []

    def get_latest_response(
        self, apparent_encoding: bool = True
    ) -> requests.Response:
        """Get latest response

        Returns:
            requests.Response: latest response
        """
        request_sucess = False
        retry_num = 0

        while not request_sucess:
            try:
                # Connect to the URL
                response = requests.get(
                    self.check_url,
                    headers={
                        "User-Agent": (
                            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5)"
                            " AppleWebKit/537.36 (KHTML, like Gecko)"
                            " Chrome/50.0.2661.102 Safari/537.36"
                        )
                    },
                )
                if response.status_code == 200:
                    # override encoding by real educated guess as provided by chardet
                    if apparent_encoding:
                        response.encoding = response.apparent_encoding
                    request_sucess = True
                else:
                    time.sleep(self.retry_interval)
            except requests.exceptions.ConnectionError:
                return None
            except requests.exceptions.RequestException:
                time.sleep(self.retry_interval)
            retry_num += 1

            # break and return empty response if reach MAX_RETRY_NUM
            if retry_num >= self.max_retry_num:
                return None

        return response

    def get_latest_soup(self, apparent_encoding: bool = True) -> BeautifulSoup:
        """Get latest soup

        Returns:
            BeautifulSoup: latest soup
        """
        response = self.get_latest_response(apparent_encoding)
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


class WutuxsChecker(AbstractChapterChecker):
    """Wutuxs checker class"""

    def get_latest_chapter_list(self) -> List[Chapter]:
        """Get latest chapter list

        Returns:
            List[Chapter]: latest chapter list
        """
        soup = self.get_latest_soup()
        if not soup:
            return []

        soup = self.get_latest_soup()
        if soup is None:
            return []
        a_list = list(soup.find("table", id="at").findAll("a"))
        chapter_list = []
        for chapter_tag in a_list:
            chapter_title = chapter_tag.text
            chapter_path = chapter_tag["href"]
            chapter_url = urlunparse(
                urlparse(self.check_url)._replace(path=chapter_path)
            )
            chapter_list.append(Chapter(title=chapter_title, url=chapter_url))

        return chapter_list


class WxChecker(AbstractChapterChecker):
    """99wx checker class"""

    def get_latest_chapter_list(self) -> List[Chapter]:
        """Get latest chapter list

        Returns:
            List[Chapter]: latest chapter list
        """
        soup = self.get_latest_soup()
        if not soup:
            return []

        soup = self.get_latest_soup()
        if soup is None:
            return []
        a_list = list(soup.find("div", id="play_0").findAll("a"))
        chapter_list = []
        for chapter_tag in a_list:
            chapter_title = chapter_tag.text
            chapter_path = chapter_tag["href"]
            chapter_url = urlunparse(
                urlparse(self.check_url)._replace(path=chapter_path)
            )
            chapter_list.append(Chapter(title=chapter_title, url=chapter_url))

        return chapter_list


class SyosetuChecker(AbstractChapterChecker):
    """Syosetu checker class"""

    def get_latest_chapter_list(self) -> List[Chapter]:
        """Get latest chapter list

        Returns:
            List[Chapter]: latest chapter list
        """
        soup = self.get_latest_soup()
        if not soup:
            return []

        dl_list = list(soup.find("div", {"class": "index_box"}).findAll("a"))
        chapter_list = []
        for chapter_tag in dl_list:
            chapter_title = chapter_tag.text
            chapter_path = chapter_tag["href"]
            chapter_url = urlunparse(
                urlparse(self.check_url)._replace(path=chapter_path)
            )
            chapter_list.append(Chapter(title=chapter_title, url=chapter_url))

        return chapter_list


class ManhuaguiChecker(AbstractChapterChecker):
    """Manhuagui chapter list"""

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
            one_a_tag = a_tags[i]

            try:
                chapter_path = one_a_tag["href"]
                if chapter_path.startswith(comic_path):
                    chapter_title = one_a_tag.text
                    chapter_url = urlunparse(
                        urlparse(self.check_url)._replace(path=chapter_path)
                    )
                    chapter_list.append(
                        Chapter(title=chapter_title, url=chapter_url)
                    )
            except KeyError:
                pass

        return chapter_list[::-1]


class QimanChecker(AbstractChapterChecker):
    """QimanChecker"""

    def get_latest_chapter_list(self) -> List[Chapter]:
        """Get latest chapter list from qiman

        Returns:
            List[Chapter]: latest chapter list
        """
        url_parse = urlparse(self.check_url)
        api_url = urlunparse(url_parse._replace(path="/bookchapter/"))

        comic_id = int(urlparse(self.check_url).path.strip("/"))

        # Send with POST method
        response = requests.post(
            api_url,
            data={"id": comic_id, "id2": 1},
        )
        if response.status_code == 200:
            """Sample response:
            [
                {
                    "id": "886859",
                    "name": "周刊136话"
                },
                {
                    "id": "886858",
                    "name": "周刊135话"
                },
                {
                    "id": "886857",
                    "name": "周刊134话"
                },
                ...
            ]
            """
            chapter_list = []
            for chapter_obj in response.json():
                chapter_id = chapter_obj["id"]
                chapter_url = urlunparse(
                    url_parse._replace(path=f"/{comic_id}/{chapter_id}.html")
                )
                chapter_list.append(
                    Chapter(title=chapter_obj["name"], url=chapter_url)
                )
            return chapter_list[::-1]

        return []


class BaozimhChecker(AbstractChapterChecker):
    """Baozimh checker"""

    def get_latest_chapter_list(self) -> List[Chapter]:
        """Get latest chapter list from baozimh

        Returns:
            List[Chapter]: latest chapter list
        """
        soup = self.get_latest_soup(apparent_encoding=False)
        if soup is None:
            return []

        a_list = [
            a.findAll("a", {"class": "comics-chapters__item"})
            for a in soup.findAll("div", {"class": "pure-g"})[1]
        ]
        chapter_list = []
        for chapter_tag in a_list:
            chapter_title = chapter_tag[0].text
            chapter_path = chapter_tag[0]["href"]
            chapter_url = urlunparse(
                urlparse(self.check_url)._replace(path=chapter_path)
            )
            chapter_list.append(Chapter(title=chapter_title, url=chapter_url))

        return chapter_list[::-1]


class XbiqugeChecker(AbstractChapterChecker):
    """Xbiquge checker"""

    def get_latest_chapter_list(self) -> List[Chapter]:
        """Get latest chapter list from xbiquge

        Returns:
            List[Chapter]: latest chapter list
        """
        soup = self.get_latest_soup()
        if soup is None:
            return []
        a_list = list(soup.find("div", id="list").findAll("a"))
        chapter_list = []
        for chapter_tag in a_list:
            chapter_title = chapter_tag.text
            chapter_path = chapter_tag["href"]
            chapter_url = urlunparse(
                urlparse(self.check_url)._replace(path=chapter_path)
            )
            chapter_list.append(Chapter(title=chapter_title, url=chapter_url))

        return chapter_list