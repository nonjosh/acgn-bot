"""Checker for Bilibili channel list pages.

Example URLs:
    https://space.bilibili.com/690151424/lists/8495686?type=season
    https://space.bilibili.com/690151424/lists/123456?type=series

APIs used:
    Season: https://api.bilibili.com/x/polymer/web-space/seasons_archives_list
    Series: https://api.bilibili.com/x/series/archives
"""

from typing import List, Optional, Tuple
from urllib.parse import parse_qs, urlparse

from helpers.chapter import Chapter
from helpers.checkers.base import AbstractChapterChecker


class BilibiliChannelSeriesChecker(AbstractChapterChecker):
    """Bilibili channel list checker."""

    URL_SUBSTRING = "space.bilibili.com/"
    SEASON_TYPE = "season"
    SERIES_TYPE = "series"
    PAGE_SIZE = 100
    SEASON_API_URL = (
        "https://api.bilibili.com/x/polymer/web-space/seasons_archives_list"
    )
    SERIES_API_URL = "https://api.bilibili.com/x/series/archives"

    def __init__(self, check_url: str) -> None:
        super().__init__(check_url)
        self.headers = {
            **self.headers,
            "Referer": check_url,
            "Origin": "https://space.bilibili.com",
            "Accept": "application/json, text/plain, */*",
        }

    @staticmethod
    def _extract_channel_info(url: str) -> Optional[Tuple[str, str, Optional[str]]]:
        parsed = urlparse(url)
        if parsed.netloc != "space.bilibili.com":
            return None

        segments = [segment for segment in parsed.path.split("/") if segment]
        if len(segments) < 3 or segments[1] != "lists":
            return None

        mid, list_id = segments[0], segments[2]
        if not mid.isdigit() or not list_id.isdigit():
            return None

        raw_type = (parse_qs(parsed.query).get("type") or [None])[0]
        list_type = raw_type.lower() if isinstance(raw_type, str) else None
        if list_type not in {
            BilibiliChannelSeriesChecker.SEASON_TYPE,
            BilibiliChannelSeriesChecker.SERIES_TYPE,
        }:
            list_type = None

        return mid, list_id, list_type

    @staticmethod
    def _chapter_sort_key(chapter_obj: dict) -> Tuple[int, str]:
        timestamp = chapter_obj.get("pubdate") or chapter_obj.get("ctime") or 0
        try:
            normalized_timestamp = int(timestamp)
        except (TypeError, ValueError):
            normalized_timestamp = 0

        chapter_id = str(chapter_obj.get("bvid") or chapter_obj.get("aid") or "")
        return normalized_timestamp, chapter_id

    @staticmethod
    def _build_chapter_url(chapter_obj: dict) -> Optional[str]:
        bvid = chapter_obj.get("bvid")
        if bvid:
            return f"https://www.bilibili.com/video/{bvid}"

        aid = chapter_obj.get("aid")
        if aid:
            return f"https://www.bilibili.com/video/av{aid}"

        return None

    def _build_api_url(self, mid: str, list_id: str, list_type: str, page_num: int) -> str:
        if list_type == self.SEASON_TYPE:
            return (
                f"{self.SEASON_API_URL}?mid={mid}&season_id={list_id}"
                f"&sort_reverse=true&page_num={page_num}&page_size={self.PAGE_SIZE}"
            )

        return (
            f"{self.SERIES_API_URL}?mid={mid}&series_id={list_id}"
            f"&pn={page_num}&ps={self.PAGE_SIZE}"
        )

    def _fetch_archives_page(
        self, mid: str, list_id: str, list_type: str, page_num: int
    ) -> Optional[Tuple[List[dict], Optional[int]]]:
        response = self.get_latest_response(
            url=self._build_api_url(mid, list_id, list_type, page_num),
            apparent_encoding=False,
        )
        if response is None:
            return None

        try:
            payload = response.json()
        except ValueError:
            return None

        if not isinstance(payload, dict) or payload.get("code") != 0:
            return None

        data = payload.get("data") or {}
        if not isinstance(data, dict):
            return None

        archives = data.get("archives") or []
        if not isinstance(archives, list):
            archives = []

        total = (data.get("page") or {}).get("total")
        try:
            total_items = int(total) if total is not None else None
        except (TypeError, ValueError):
            total_items = None

        normalized_archives = [item for item in archives if isinstance(item, dict)]
        return normalized_archives, total_items

    def _get_chapter_list_for_type(
        self, mid: str, list_id: str, list_type: str
    ) -> List[Chapter]:
        all_archives: List[dict] = []
        page_num = 1

        while True:
            page_data = self._fetch_archives_page(mid, list_id, list_type, page_num)
            if page_data is None:
                return []

            archives, total_items = page_data
            if not archives:
                break

            all_archives.extend(archives)

            if total_items is not None and page_num * self.PAGE_SIZE >= total_items:
                break
            if len(archives) < self.PAGE_SIZE:
                break

            page_num += 1

        chapter_list: List[Chapter] = []
        seen_urls: set[str] = set()
        for chapter_obj in sorted(all_archives, key=self._chapter_sort_key):
            chapter_url = self._build_chapter_url(chapter_obj)
            if not chapter_url or chapter_url in seen_urls:
                continue

            seen_urls.add(chapter_url)
            title = str(chapter_obj.get("title") or "").strip()
            chapter_list.append(Chapter(title=title or chapter_url, url=chapter_url))

        return chapter_list

    def get_latest_chapter_list(self) -> List[Chapter]:
        """Get latest chapter list from Bilibili channel list APIs."""
        channel_info = self._extract_channel_info(self.check_url)
        if channel_info is None:
            return []

        mid, list_id, list_type = channel_info
        candidate_types = (
            [list_type]
            if list_type is not None
            else [self.SEASON_TYPE, self.SERIES_TYPE]
        )

        for candidate_type in candidate_types:
            chapter_list = self._get_chapter_list_for_type(
                mid=mid,
                list_id=list_id,
                list_type=candidate_type,
            )
            if chapter_list or list_type is not None:
                return chapter_list

        return []