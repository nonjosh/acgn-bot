from typing import List
from urllib.parse import urlparse, urlunparse
from helpers.chapter import Chapter
from helpers.checkers.base import AbstractChapterChecker


class Mn4uChecker(AbstractChapterChecker):
    """Mn4u checker"""

    def __init__(self, check_url: str) -> None:
        super().__init__(check_url)
        self.headers["referer"] = self.check_url
        mid = urlparse(self.check_url).path.strip("/").split("-")[1]
        self.params = {"mid": mid}
        self.check_url = "https://mn4u.net/app/manga/controllers/cont.listChapter.php"

    def get_latest_chapter_list(self) -> List[Chapter]:
        """Get latest chapter list from mn4u

        Returns:
            List[Chapter]: latest chapter list
        """
        soup = self.get_latest_soup()
        if soup is None:
            return []
        a_list = list(soup.find("ul", {"class": "list-chapters"}).findAll("a"))
        chapter_list = []
        for chapter_tag in a_list:
            chapter_title = chapter_tag.find("div", {"class": "chapter-name"}).text
            chapter_path = chapter_tag["href"]
            chapter_url = urlunparse(
                urlparse(self.check_url)._replace(path=chapter_path)
            )
            chapter_list.append(Chapter(title=chapter_title, url=chapter_url))

        # Reverse the list to get the latest chapter first
        return chapter_list[::-1]
