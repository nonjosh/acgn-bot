import os
from typing import List
from urllib.parse import urlparse, urlunparse

import requests
from bs4 import BeautifulSoup
from bs4.element import Tag

from helpers.chapter import Chapter
from helpers.checkers.base import AbstractChapterChecker
from helpers.utils import get_logger

logger = get_logger(__name__)


class SyosetuChecker(AbstractChapterChecker):
    """Syosetu checker class"""

    URL_SUBSTRING = "syosetu"

    def __init__(self, check_url: str) -> None:
        super().__init__(check_url)
        # Syosetu blocks datacenter IPs (GCP etc.) with 403; route through a
        # proxy (e.g. Tailscale exit node SOCKS5) when provided.
        proxy = os.getenv("SYOSETU_PROXY")
        if proxy:
            self.proxies = {"http": proxy, "https": proxy}

    def get_latest_response(self, url: str = None, apparent_encoding: bool = True):
        # Deterministic failures (403 from datacenter IP / blocked UA) are not
        # retried: log a concise error instead of raising with a traceback.
        try:
            return super().get_latest_response(url=url, apparent_encoding=apparent_encoding)
        except requests.exceptions.RequestException as err:
            logger.error(
                "syosetu request failed (via proxy: %s): %s", bool(self.proxies), err
            )
            return None

    def get_latest_soup(self, apparent_encoding: bool = True):
        # Proxy down (e.g. home desktop off) surfaces here as a silent None;
        # log one concise line instead.
        soup = super().get_latest_soup(apparent_encoding=apparent_encoding)
        if not soup:
            logger.error(
                "syosetu unreachable (via proxy: %s): %s",
                bool(self.proxies),
                self.check_url,
            )
        return soup

    def get_latest_chapter_list(self) -> List[Chapter]:
        """Get latest chapter list

        Automatically follows the last-page pagination link so the base URL
        (e.g. https://ncode.syosetu.com/n2819ha/) can be used without needing
        to manually specify a ``?p=N`` query parameter.

        Returns:
            List[Chapter]: latest chapter list
        """
        soup = self.get_latest_soup()
        if not soup:
            return []

        # If there are multiple pages, follow the "last page" link so we always
        # parse the most recent chapters regardless of how many pages exist.
        last_page_tag = soup.find("a", {"class": "c-pager__item--last"})
        if last_page_tag:
            last_page_path = last_page_tag["href"]
            last_page_url = urlunparse(
                urlparse(self.check_url)._replace(
                    path=last_page_path.split("?")[0],
                    query=last_page_path.split("?")[1] if "?" in last_page_path else "",
                )
            )
            response = self.get_latest_response(url=last_page_url)
            if response:
                soup = BeautifulSoup(response.text, "html.parser")

        dl_list: List[Tag] = list(soup.find_all("a", {"class": "p-eplist__subtitle"}))
        chapter_list = []
        for chapter_tag in dl_list:
            chapter_title = chapter_tag.text.strip()
            chapter_path = chapter_tag["href"]
            chapter_url = urlunparse(
                urlparse(self.check_url)._replace(path=chapter_path)
            )
            chapter_list.append(Chapter(title=chapter_title, url=chapter_url))

        return chapter_list
