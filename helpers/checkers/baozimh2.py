from typing import List

import requests
from bs4.element import Tag
from chinese_converter import to_traditional

from helpers.chapter import Chapter
from helpers.checkers.base import AbstractChapterChecker


class Baozimh2Checker(AbstractChapterChecker):
    """baozimh.org checker
    sample API: https://api-get-v3.mgsearcher.com/api/manga/get?mid=510
    sample comic page: https://baozimh.org/manga/zhangmendidiaodian-yuewenmanhua
    expected format in config: https://api-get-v3.mgsearcher.com/api/manga/get?mid=510&name=zhangmendidiaodian-yuewenmanhua
    """

    URL_SUBSTRING = "mgsearcher"

    def get_latest_chapter_list(self) -> List[Chapter]:
        """Get latest chapter list from baozimh

        Returns:
            List[Chapter]: latest chapter list
        """
        response = requests.get(self.check_url)

        chapters: list[dict] = response.json().get("data", {}).get("chapters", [])
        comic_name = self.check_url.split("name=")[-1]

        chapter_list: List[Chapter] = []
        for chapter in chapters:

            chapter_title = chapter["attributes"]["title"]
            chapter_title = to_traditional(chapter_title)
            chapter_slug = chapter["attributes"]["slug"]
            chapter_url = f"https://baozimh.org/manga/{comic_name}/{chapter_slug}"
            chapter_list.append(Chapter(title=chapter_title, url=chapter_url))

        return chapter_list
