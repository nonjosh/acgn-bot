import time
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

        api_url = f"https://api-get-v3.mgsearcher.com/api/manga/get?mid={mid}&mode=all"
        self.headers.update(
            {"Origin": "https://baozimh.org"}
        )  # This is needed for fetching latest chapters...
        api_response = None
        for attempt in range(self.max_retry_num):
            api_response = self.get_latest_response(url=api_url, apparent_encoding=False)
            if api_response is not None:
                break
            if attempt < self.max_retry_num - 1:
                time.sleep(self.retry_interval)

        if api_response is None:
            return []

        try:
            payload = api_response.json()
        except ValueError:
            return []

        if not isinstance(payload, dict):
            return []

        chapters: list[dict] = payload.get("data", {}).get("chapters", [])
        if not isinstance(chapters, list):
            return []

        chapter_list: List[Chapter] = []
        for chapter in chapters:
            attributes = chapter.get("attributes", {}) if isinstance(chapter, dict) else {}
            chapter_title = attributes.get("title")
            chapter_slug = attributes.get("slug")
            if not chapter_title or not chapter_slug:
                continue
            chapter_title = to_traditional(chapter_title)
            chapter_url = f"https://baozimh.org/manga/{comic_name}/{chapter_slug}"
            chapter_list.append(Chapter(title=chapter_title, url=chapter_url))

        return chapter_list
