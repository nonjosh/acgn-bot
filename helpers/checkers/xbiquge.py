from typing import List
from urllib.parse import urljoin

from bs4.element import Tag

from helpers.chapter import Chapter
from helpers.checkers.base import AbstractChapterChecker


class XbiqugeChecker(AbstractChapterChecker):
    """Xbiquge checker"""

    URL_SUBSTRING = "xbiquge"

    def get_latest_chapter_list(self) -> List[Chapter]:
        """Get latest chapter list from xbiquge

        Returns:
            List[Chapter]: latest chapter list
        """
        soup = self.get_latest_soup()
        if soup is None:
            return []
        a_list: List[Tag] = list(
            soup.find("ul", class_="section-list fix").findAll("a")
        )
        chapter_list = []
        for chapter_tag in a_list:
            chapter_title = chapter_tag.text
            chapter_path = chapter_tag["href"]
            chapter_url = urljoin(self.check_url, chapter_path)
            chapter_list.append(Chapter(title=chapter_title, url=chapter_url))

        # Remove duplicated
        chapter_list = list(set(chapter_list))

        # Sort by chapter url
        chapter_list.sort(key=lambda x: x.url)
        return chapter_list
