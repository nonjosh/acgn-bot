from typing import List
from urllib.parse import urlparse, urlunparse

from bs4.element import Tag

from helpers.chapter import Chapter
from helpers.checkers.base import AbstractChapterChecker


class KunmangaChecker(AbstractChapterChecker):
    """Kunmanga checker"""

    URL_SUBSTRING = "kunmanga"

    def get_latest_chapter_list(self) -> List[Chapter]:
        """Get latest chapter list from Kunmanga

        Returns:
            List[Chapter]: latest chapter list
        """
        soup = self.get_latest_soup()
        if soup is None:
            return []
        li_list: List[Tag] = soup.find_all("li", {"class": "wp-manga-chapter"})
        a_list = [li.find("a") for li in li_list if li.find("a") is not None]
        chapter_list = []
        for chapter_tag in a_list:
            chapter_title = chapter_tag.text.strip()
            chapter_url = chapter_tag["href"]
            chapter_list.append(Chapter(title=chapter_title, url=chapter_url))

        return chapter_list[::-1]
