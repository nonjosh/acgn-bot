from typing import List
from urllib.parse import urlparse, urlunparse
from helpers.chapter import Chapter
from helpers.checkers.base import AbstractChapterChecker


class KlmanagaChecker(AbstractChapterChecker):
    """Klmanaga checker"""

    URL_SUBSTRING = "mangakl"

    def get_latest_chapter_list(self) -> List[Chapter]:
        """Get latest chapter list from klmanga

        Returns:
            List[Chapter]: latest chapter list
        """
        soup = self.get_latest_soup()
        if soup is None:
            return []
        a_list = list(soup.find("div", id="list-chapter").findAll("a"))
        chapter_list = []
        for chapter_tag in a_list:
            if chapter_tag.get("title"):
                chapter_title = chapter_tag["title"]
                chapter_path = chapter_tag["href"]
                chapter_url = urlunparse(
                    urlparse(self.check_url)._replace(path=chapter_path)
                )
                chapter_list.append(Chapter(title=chapter_title, url=chapter_url))

        # Reverse the list to get the latest chapter first
        return chapter_list[::-1]
