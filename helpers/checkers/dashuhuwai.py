from typing import List
from urllib.parse import urlparse, urlunparse
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
        a_list = [li.find("a") for li in soup.find(id="ul_chapter1").find_all("li")]
        chapter_list = []
        for chapter_tag in a_list:
            chapter_title = chapter_tag.text
            chapter_path = chapter_tag["href"]
            chapter_url = urlunparse(
                urlparse(self.check_url)._replace(path=chapter_path)
            )
            chapter_list.append(Chapter(title=chapter_title, url=chapter_url))

        return chapter_list
