from typing import List

from bs4.element import ResultSet, Tag

from helpers.chapter import Chapter
from helpers.checkers.base import AbstractChapterChecker


class JmangaChecker(AbstractChapterChecker):
    """Kunmanga checker"""

    URL_SUBSTRING = "jmanga"

    def get_latest_chapter_list(self) -> List[Chapter]:
        """Get latest chapter list from Jmanga

        Returns:
            List[Chapter]: latest chapter list
        """
        soup = self.get_latest_soup()
        if soup is None:
            return []
        a_list: ResultSet[Tag] = soup.find_all("a", {"class": "item-link"})
        chapter_list = []
        for chapter_tag in a_list:
            chapter_title = chapter_tag["title"]
            chapter_url = chapter_tag["href"]
            chapter_list.append(Chapter(title=chapter_title, url=chapter_url))

        return chapter_list[::-1]
