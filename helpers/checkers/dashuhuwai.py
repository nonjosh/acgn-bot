from typing import List

from bs4.element import Tag

from helpers.chapter import Chapter
from helpers.checkers.base import AbstractChapterChecker


class DashumanhuaChecker(AbstractChapterChecker):
    """Dashumanhua checker"""

    URL_SUBSTRING = "dashumanhua"

    def get_latest_chapter_list(self) -> List[Chapter]:
        """Get latest chapter list from dashumanhua

        Returns:
            List[Chapter]: latest chapter list
        """
        soup = self.get_latest_soup()
        if soup is None:
            return []
        li_list: List[Tag] = soup.find(id="ul_chapter1").find_all("li")
        a_list: List[Tag] = [li.find("a") for li in li_list if li.find("a") is not None]
        chapter_list = []
        for chapter_tag in a_list:
            chapter_title = chapter_tag.text
            chapter_url = chapter_tag["href"]
            chapter_list.append(Chapter(title=chapter_title, url=chapter_url))

        return chapter_list[::-1]
