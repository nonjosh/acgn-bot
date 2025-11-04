from typing import List

from chinese_converter import to_traditional

from helpers.chapter import Chapter
from helpers.checkers.base import AbstractChapterChecker


class Baozimh2Checker(AbstractChapterChecker):
    """baozimh.org checker
    sample API: https://api-get-v3.mgsearcher.com/api/manga/get?mid=510
    sample comic page: https://baozimh.org/manga/zhangmendidiaodian-yuewenmanhua
    expected format in config: https://baozimh.org/manga/zhangmendidiaodian-yuewenmanhua?mid=510
    """

    URL_SUBSTRING = "baozimh.org"

    def get_latest_chapter_list(self) -> List[Chapter]:
        """Get latest chapter list from baozimh

        Returns:
            List[Chapter]: latest chapter list
        """
        mid = self.check_url.split("mid=")[-1]
        comic_name = self.check_url.split("/manga/")[1].split("?")[0]

        api_url = f"https://api-get-v3.mgsearcher.com/api/manga/get?mid={mid}"
        api_response = self.get_latest_response(url=api_url, apparent_encoding=False)

        chapters: list[dict] = api_response.json().get("data", {}).get("chapters", [])

        chapter_list: List[Chapter] = []
        for chapter in chapters:

            chapter_title = chapter["attributes"]["title"]
            chapter_title = to_traditional(chapter_title)
            chapter_slug = chapter["attributes"]["slug"]
            chapter_url = f"https://baozimh.org/manga/{comic_name}/{chapter_slug}"
            chapter_list.append(Chapter(title=chapter_title, url=chapter_url))

        return chapter_list
