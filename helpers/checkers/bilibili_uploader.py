"""Checker for Bilibili uploader keyword search.

Example URL:
    https://space.bilibili.com/154244413/upload/video?keyword=转生重骑士

APIs used:
    https://api.bilibili.com/x/web-interface/search/type?search_type=video&keyword=...
    Results are filtered to the uploader's mid after fetching.
"""

import re
from typing import List, Optional, Tuple
from urllib.parse import parse_qs, quote, urlparse

from chinese_converter import to_simplified

from helpers.chapter import Chapter
from helpers.checkers.base import AbstractChapterChecker


class BilibiliUploaderChecker(AbstractChapterChecker):
    """Bilibili uploader keyword search checker."""

    URL_SUBSTRING = "/upload/video"
    SEARCH_API_URL = "https://api.bilibili.com/x/web-interface/search/type"
    HOME_URL = "https://www.bilibili.com/"
    PAGE_SIZE = 20
    MAX_PAGES = 2
    EM_TAG_PATTERN = re.compile(r"<[^>]+>")

    def __init__(self, check_url: str) -> None:
        super().__init__(check_url)
        self.headers = {
            **self.headers,
            "User-Agent": (
                "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"
            ),
            "Referer": "https://search.bilibili.com/",
            "Accept": "application/json, text/plain, */*",
        }

    @staticmethod
    def _extract_info(url: str) -> Optional[Tuple[str, str]]:
        parsed = urlparse(url)
        if parsed.netloc != "space.bilibili.com":
            return None

        segments = [segment for segment in parsed.path.split("/") if segment]
        if len(segments) < 2 or segments[1] != "upload":
            return None

        mid = segments[0]
        if not mid.isdigit():
            return None

        query = parse_qs(parsed.query)
        keyword = (query.get("keyword") or query.get("kw") or [None])[0]
        if not keyword or not keyword.strip():
            return None

        return mid, to_simplified(keyword.strip())

    def _sync_bilibili_cookies(self) -> None:
        """Seed buvid3 cookie required by the search API."""
        response = self.get_latest_response(url=self.HOME_URL)
        if response is None:
            return

        set_cookie = response.headers.get("set-cookie", "")
        cookies = [
            fragment.split(";")[0].strip()
            for fragment in set_cookie.split(",")
        ]
        cookies = [c for c in cookies if c.startswith(("buvid3=", "b_nut="))]
        if cookies:
            self.headers["Cookie"] = "; ".join(cookies)

    def _search_page(self, keyword: str, page_num: int) -> List[dict]:
        url = (
            f"{self.SEARCH_API_URL}?search_type=video"
            f"&keyword={quote(keyword, safe='')}&page={page_num}"
        )
        response = self.get_latest_response(url=url, apparent_encoding=False)
        if response is None:
            return []

        try:
            payload = response.json()
        except ValueError:
            return []

        if not isinstance(payload, dict) or payload.get("code") != 0:
            return []

        data = payload.get("data") or {}
        results = data.get("result") or []
        if not isinstance(results, list):
            return []

        return [item for item in results if isinstance(item, dict)]

    @staticmethod
    def _clean_title(title: str) -> str:
        return BilibiliUploaderChecker.EM_TAG_PATTERN.sub(
            "", str(title or "")
        ).strip()

    def _build_chapter_list(
        self, mid: str, keyword: str
    ) -> List[Chapter]:
        chapters: List[Chapter] = []
        seen_urls: set[str] = set()

        all_results: List[dict] = []
        for page_num in range(1, self.MAX_PAGES + 1):
            results = self._search_page(keyword=keyword, page_num=page_num)
            if not results:
                break
            all_results.extend(results)
            if len(results) < self.PAGE_SIZE:
                break

        for item in sorted(
            all_results, key=lambda item: item.get("pubdate") or 0
        ):
            if str(item.get("mid") or item.get("account_id")) != mid:
                continue

            bvid = item.get("bvid")
            if bvid:
                chapter_url = f"https://www.bilibili.com/video/{bvid}"
            elif item.get("aid"):
                chapter_url = f"https://www.bilibili.com/video/av{item['aid']}"
            else:
                continue
            if chapter_url in seen_urls:
                continue

            seen_urls.add(chapter_url)
            title = self._clean_title(item.get("title"))
            chapters.append(Chapter(title=title or chapter_url, url=chapter_url))

        return chapters

    def get_latest_chapter_list(self) -> List[Chapter]:
        """Get latest chapter list from Bilibili search API."""
        info = self._extract_info(self.check_url)
        if info is None:
            return []

        mid, keyword = info
        self._sync_bilibili_cookies()
        return self._build_chapter_list(mid=mid, keyword=keyword)
