from typing import List
from urllib.parse import urlparse, urlunparse

from bs4.element import ResultSet, Tag

from helpers.chapter import Chapter
from helpers.checkers.base import AbstractChapterChecker


class LinovelibChecker(AbstractChapterChecker):
    """Linovelib checker"""

    URL_SUBSTRING = "linovelib"

    def get_latest_chapter_list(self) -> List[Chapter]:
        """Get latest chapter list from klmanga

        Returns:
            List[Chapter]: latest chapter list
        """
        soup = self.get_latest_soup()
        if soup is None:
            return []
        a_list: ResultSet[Tag] = soup.find_all("a", {"class": "chapter-li-a"})
        chapter_list = []
        for chapter_tag in a_list:
            chapter_span = chapter_tag.find("span", {"class": "chapter-index"})
            chapter_title = chapter_span.text.strip()
            chapter_path = chapter_tag["href"]
            chapter_url = urlunparse(
                urlparse(self.check_url)._replace(path=chapter_path)
            )
            chapter_list.append(Chapter(title=chapter_title, url=chapter_url))

        # Reverse the list to get the latest chapter first
        return chapter_list
