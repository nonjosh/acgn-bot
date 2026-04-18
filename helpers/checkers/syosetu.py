from typing import List
from urllib.parse import urlparse, urlunparse

from bs4 import BeautifulSoup
from bs4.element import Tag

from helpers.chapter import Chapter
from helpers.checkers.base import AbstractChapterChecker


class SyosetuChecker(AbstractChapterChecker):
    """Syosetu checker class"""

    URL_SUBSTRING = "syosetu"

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
