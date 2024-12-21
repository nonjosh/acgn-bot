from typing import List
from urllib.parse import urlparse, urlunparse

from chinese_converter import to_traditional

from helpers.chapter import Chapter
from helpers.checkers.base import AbstractChapterChecker


class BiquChecker(AbstractChapterChecker):
    """Biqu checker"""

    URL_SUBSTRING = "m.biqu520.net"

    def get_latest_chapter_list(self) -> List[Chapter]:
        """Get latest chapter list from baozimh

        Returns:
            List[Chapter]: latest chapter list
        """
        soup = self.get_latest_soup()
        if soup is None:
            return []

        ul = soup.find("ul", {"class": "chapter"})
        a_list = ul.findAll("a")
        chapter_list = []
        for chapter_tag in a_list:
            chapter_title = to_traditional(chapter_tag.text)
            chapter_path = chapter_tag["href"]
            chapter_url = urlunparse(
                urlparse(self.check_url)._replace(path=chapter_path)
            )
            chapter_list.append(Chapter(title=chapter_title, url=chapter_url))

        return chapter_list[::-1]
