"""Checker for Mangaraw manga pages.

Example manga URL:
    https://mangaraw.co.uk/manga/2439

API used:
    https://api.mangarw.com/api/v1/manga/2439/chapters
"""

from typing import List, Optional, Tuple
from urllib.parse import urlparse

from helpers.chapter import Chapter
from helpers.checkers.base import AbstractChapterChecker


class MangarawChecker(AbstractChapterChecker):
    """Mangaraw checker."""

    URL_SUBSTRING = "mangaraw.co.uk/manga/"
    API_BASE_URL = "https://api.mangarw.com"

    def __init__(self, check_url: str) -> None:
        super().__init__(check_url)
        self.headers = {
            **self.headers,
            "Referer": check_url,
            "Accept": "application/json, text/plain, */*",
        }

    @staticmethod
    def _extract_manga_id(url: str) -> Optional[str]:
        parsed = urlparse(url)
        segments = [segment for segment in parsed.path.split("/") if segment]
        if len(segments) < 2 or segments[0] != "manga":
            return None

        manga_id = segments[1]
        if not manga_id.isdigit():
            return None

        return manga_id

    @staticmethod
    def _chapter_sort_key(chapter_obj: dict) -> Tuple[int, float]:
        index = chapter_obj.get("index")
        if index is not None:
            try:
                return (0, float(index))
            except (TypeError, ValueError):
                pass

        chapter_id = chapter_obj.get("id")
        try:
            return (1, float(chapter_id))
        except (TypeError, ValueError):
            return (2, 0.0)

    def get_latest_chapter_list(self) -> List[Chapter]:
        """Get latest chapter list from Mangaraw.

        Returns:
            List[Chapter]: chapter list ordered from oldest to newest
        """
        manga_id = self._extract_manga_id(self.check_url)
        if not manga_id:
            return []

        response = self.get_latest_response(
            url=f"{self.API_BASE_URL}/api/v1/manga/{manga_id}/chapters",
            apparent_encoding=False,
        )
        if response is None:
            return []

        try:
            payload = response.json()
        except ValueError:
            return []

        chapter_data = payload.get("data", []) if isinstance(payload, dict) else []
        if not isinstance(chapter_data, list):
            return []

        parsed = urlparse(self.check_url)
        chapter_base_url = f"{parsed.scheme}://{parsed.netloc}"
        chapter_list: List[Chapter] = []

        for chapter_obj in sorted(
            [item for item in chapter_data if isinstance(item, dict)],
            key=self._chapter_sort_key,
        ):
            chapter_id = chapter_obj.get("id")
            if chapter_id is None:
                continue

            chapter_url = f"{chapter_base_url}/chapter/{chapter_id}"
            title = str(chapter_obj.get("title") or "").strip()
            chapter_list.append(Chapter(title=title or chapter_url, url=chapter_url))

        return chapter_list
