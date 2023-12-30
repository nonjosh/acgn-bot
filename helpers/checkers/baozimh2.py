from typing import List
from bs4.element import Tag
from helpers.chapter import Chapter
from helpers.checkers.base import AbstractChapterChecker


class Baozimh2Checker(AbstractChapterChecker):
    """Baozimh checker"""

    URL_SUBSTRING = "baozimh.org"

    def get_latest_chapter_list(self) -> List[Chapter]:
        """Get latest chapter list from baozimh

        Returns:
            List[Chapter]: latest chapter list
        """
        soup = self.get_latest_soup()
        if soup is None:
            return []

        li_list: List[Tag] = soup.find_all("div", {"class": "chapteritem"})
        a_list = [li.find("a") for li in li_list]
        chapter_list = []
        for chapter_tag in a_list:
            chapter_title = chapter_tag.find(
                "span", {"class": "chaptertitle"}
            ).text.strip()
            chapter_url = chapter_tag["href"]
            chapter_list.append(Chapter(title=chapter_title, url=chapter_url))

            return chapter_list[::-1]
        return []
