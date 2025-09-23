from typing import List
from urllib.parse import urlparse, urlunparse

from bs4.element import Tag
from chinese_converter import to_simplified

from helpers.chapter import Chapter
from helpers.checkers.base import AbstractChapterChecker


class BaozimhChecker(AbstractChapterChecker):
    """Baozimh checker"""

    URL_SUBSTRING = "baozimh.com"

    def get_latest_chapter_list(self) -> List[Chapter]:
        """Get latest chapter list from baozimh

        Returns:
            List[Chapter]: latest chapter list
        """
        soup = self.get_latest_soup(apparent_encoding=False)
        if soup is None:
            return []

        pure_g_div_list: List[Tag] = soup.findAll("div", {"class": "pure-g"})

        # Find which div contains chapter items
        for pure_g_div in pure_g_div_list:
            chapter_links = pure_g_div.findAll("a", {"class": "comics-chapters__item"})
            if chapter_links:
                chapter_list = []
                for link in chapter_links:
                    chapter_title = to_simplified(link.text)
                    chapter_path = link["href"]
                    chapter_url = urlunparse(
                        urlparse(self.check_url)._replace(path=chapter_path)
                    )
                    chapter_list.append(Chapter(title=chapter_title, url=chapter_url))

                chapter_list.sort(key=lambda c: c.title)
                return chapter_list
        return []
