from typing import List
from helpers.chapter import Chapter
from helpers.checkers.base import AbstractChapterChecker


class SixNineShuBaChecker(AbstractChapterChecker):
    """69shu checker class"""

    URL_SUBSTRING = "69shu"

    def get_latest_chapter_list(self) -> List[Chapter]:
        """Get latest chapter list

        Returns:
            List[Chapter]: latest chapter list
        """
        soup = self.get_latest_soup()
        if not soup:
            return []

        dl_list = list(soup.find("div", {"class": "qustime"}).findAll("a"))
        chapter_list = []
        for chapter_tag in dl_list:
            chapter_title = chapter_tag.find("span").text
            chapter_url = chapter_tag["href"]
            chapter_list.append(Chapter(title=chapter_title, url=chapter_url))

        return chapter_list
