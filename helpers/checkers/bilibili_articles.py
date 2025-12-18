"""Checker for Bilibili readlist (专栏文集) pages.

Example readlist URL:
    https://www.bilibili.com/read/readlist/rl812409

API used:
    https://api.bilibili.com/x/article/list/web/articles?id=812409

Chapter URL is constructed from `dyn_id_str`:
    https://www.bilibili.com/opus/<dyn_id_str>
"""

import re
from typing import List, Optional
from urllib.parse import urlparse

from helpers.chapter import Chapter
from helpers.checkers.base import AbstractChapterChecker


class BilibiliArticlesChecker(AbstractChapterChecker):
    """Bilibili readlist checker."""

    URL_SUBSTRING = "bilibili.com/read/readlist"

    _READLIST_ID_RE = re.compile(r"rl(?P<id>\d+)")

    @staticmethod
    def _extract_readlist_id(url: str) -> Optional[str]:
        parsed = urlparse(url)
        # Common form: /read/readlist/rl812409
        match = BilibiliArticlesChecker._READLIST_ID_RE.search(parsed.path)
        if match:
            return match.group("id")

        # Fallback: last path segment might be digits
        segments = [seg for seg in parsed.path.split("/") if seg]
        if segments:
            last = segments[-1]
            if last.isdigit():
                return last

        return None

    def __init__(self, check_url: str) -> None:
        super().__init__(check_url)

        # Bilibili endpoints can be sensitive to missing Referer.
        self.headers = {
            **self.headers,
            "Referer": check_url,
            "Accept": "application/json, text/plain, */*",
        }

    def get_latest_chapter_list(self) -> List[Chapter]:
        """Fetch chapter list from Bilibili readlist API.

        Returns:
            List[Chapter]: chapter list ordered from oldest to newest
        """
        try:
            readlist_id = self._extract_readlist_id(self.check_url)
            if not readlist_id:
                return []

            api_url = "https://api.bilibili.com/x/article/list/web/articles"
            response = self.get_latest_response(
                url=f"{api_url}?id={readlist_id}", apparent_encoding=False
            )
            if response is None:
                return []

            payload = response.json() if response else None
            if not isinstance(payload, dict) or payload.get("code") != 0:
                return []

            data = payload.get("data") or {}
            articles = data.get("articles") or []
            if not isinstance(articles, list) or len(articles) == 0:
                return []

            # API appears to already return ascending order, but sort defensively.
            def sort_key(item: dict) -> int:
                ts = item.get("publish_time")
                try:
                    return int(ts)
                except Exception:  # pylint: disable=broad-except
                    return 0

            chapter_list: List[Chapter] = []
            for item in sorted(
                [a for a in articles if isinstance(a, dict)], key=sort_key
            ):
                dyn_id_str = item.get("dyn_id_str")
                title = (item.get("title") or "").strip()
                if not dyn_id_str:
                    continue
                chapter_url = f"https://www.bilibili.com/opus/{dyn_id_str}"
                chapter_list.append(
                    Chapter(title=title or chapter_url, url=chapter_url)
                )

            return chapter_list
        except Exception:  # pylint: disable=broad-except
            return []
