from typing import List
from urllib.parse import urlparse, urlunparse
from bs4.element import Tag
from helpers.chapter import Chapter
from helpers.checkers.base import AbstractChapterChecker


class ManhuaguiChecker(AbstractChapterChecker):
    """Manhuagui chapter list"""

    URL_SUBSTRING = "manhuagui"

    def get_latest_chapter_list(self) -> List[Chapter]:
        """Get latest chapter list from manhuagui

        Returns:
            List[Chapter]: latest chapter list
        """
        soup = self.get_latest_soup()
        if not soup:
            return []

        comic_path = urlparse(self.check_url).path

        a_tags = soup.findAll("a")

        chapter_list = []
        for i in range(0, len(a_tags) - 1):  # 'a' tags are for links
            one_a_tag: Tag = a_tags[i]

            try:
                chapter_path = one_a_tag["href"]
                if chapter_path.startswith(comic_path):
                    chapter_title = one_a_tag.text
                    chapter_url = urlunparse(
                        urlparse(self.check_url)._replace(path=chapter_path)
                    )
                    chapter_list.append(Chapter(title=chapter_title, url=chapter_url))
            except KeyError:
                pass

        return chapter_list[::-1]
