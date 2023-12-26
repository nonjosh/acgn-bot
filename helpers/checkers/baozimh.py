from typing import List
from urllib.parse import urlparse, urlunparse
from helpers.chapter import Chapter
from helpers.checkers.base import AbstractChapterChecker


class BaozimhChecker(AbstractChapterChecker):
    """Baozimh checker"""

    def get_latest_chapter_list(self) -> List[Chapter]:
        """Get latest chapter list from baozimh

        Returns:
            List[Chapter]: latest chapter list
        """
        soup = self.get_latest_soup(apparent_encoding=False)
        if soup is None:
            return []

        pure_g_div_list = soup.findAll("div", {"class": "pure-g"})

        # Find which div contains chapter items
        for pure_g_div in pure_g_div_list:
            if pure_g_div.find("a", {"class": "comics-chapters__item"}):
                a_list = [
                    a.findAll("a", {"class": "comics-chapters__item"})
                    for a in pure_g_div
                ]
                chapter_list = []
                for chapter_tag in a_list:
                    chapter_title = chapter_tag[0].text
                    chapter_path = chapter_tag[0]["href"]
                    chapter_url = urlunparse(
                        urlparse(self.check_url)._replace(path=chapter_path)
                    )
                    chapter_list.append(Chapter(title=chapter_title, url=chapter_url))

                return chapter_list[::-1]
        return []
