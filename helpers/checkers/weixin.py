from typing import List
from bs4.element import Tag
from helpers.chapter import Chapter
from helpers.checkers.base import AbstractChapterChecker


class WeixinChecker(AbstractChapterChecker):
    """Weixin checker"""

    URL_SUBSTRING = "weixin.qq.com"

    def get_latest_chapter_list(self) -> List[Chapter]:
        """Get latest chapter list from baozimh

        Returns:
            List[Chapter]: latest chapter list
        """
        soup = self.get_latest_soup(apparent_encoding=False)
        if soup is None:
            return []

        li_list: Tag = soup.find_all("li", {"class": "album__list-item"})
        chapter_list = []

        # Find which div contains chapter items
        for li in li_list:
            chapter_title = li.attrs["data-title"]
            chapter_url = li.attrs["data-link"]
            chapter_list.append(Chapter(title=chapter_title, url=chapter_url))

        return chapter_list[::-1]
