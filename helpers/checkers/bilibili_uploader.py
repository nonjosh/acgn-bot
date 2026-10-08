"""Checker for Bilibili uploader keyword search.

Example URL:
    https://space.bilibili.com/154244413/upload/video?keyword=转生重骑士

APIs used:
    https://api.bilibili.com/x/web-interface/search/type?search_type=video&keyword=...
    Results are filtered to the uploader's mid after fetching.
"""

import re
import time
from typing import List, Optional, Tuple
from urllib.parse import parse_qs, quote, urlparse

import requests
from chinese_converter import to_simplified

from helpers.chapter import Chapter
from helpers.checkers.base import AbstractChapterChecker
from helpers.utils import get_logger

logger = get_logger(__name__)


class BilibiliUploaderChecker(AbstractChapterChecker):
    """Bilibili uploader keyword search checker."""

    URL_SUBSTRING = "/upload/video"
    SEARCH_API_URL = "https://api.bilibili.com/x/web-interface/search/type"
    HOME_URL = "https://www.bilibili.com/"
    FINGER_SPI_URL = "https://api.bilibili.com/x/frontend/finger/spi"
    # ponytail: class-level cookie cache = one shared "device" for all checkers;
    # re-seeding a fresh anonymous identity per run maximizes 412 risk-control flags.
    _cookie_cache: dict = {}
    COOKIE_TTL_SECONDS = 24 * 3600
    PAGE_SIZE = 20
    MAX_PAGES = 2
    EM_TAG_PATTERN = re.compile(r"<[^>]+>")

    def __init__(self, check_url: str) -> None:
        super().__init__(check_url)
        # ever-seen results: bilibili search ranking drifts between runs, so an
        # already-announced video can leave and re-enter the top pages (it was
        # raised as an update twice); keeping it in the union makes the
        # URL-based diff in the base checker never re-report it
        self._known_chapters: dict[str, Chapter] = {}
        self._known_pubdates: dict[str, int] = {}
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
        """Seed buvid3/buvid4/b_nut cookies, reused across runs so the search
        API sees one stable device instead of a fresh anonymous client each run.

        The search API requires buvid3+buvid4 (finger/spi issues both) and
        b_nut; an incomplete jar on a datacenter IP triggers 412 risk control.
        """
        cached = BilibiliUploaderChecker._cookie_cache
        if cached and time.time() - cached["ts"] < self.COOKIE_TTL_SECONDS:
            self.headers["Cookie"] = cached["cookie"]
            return

        cookies: dict = {}
        response = self.get_latest_response(url=self.HOME_URL)
        if response is not None:
            for fragment in response.headers.get("set-cookie", "").split(","):
                pair = fragment.split(";")[0].strip()
                if "=" in pair and pair.split("=", 1)[0] in ("buvid3", "buvid4", "b_nut"):
                    key, value = pair.split("=", 1)
                    cookies[key] = value

        response = self.get_latest_response(url=self.FINGER_SPI_URL)
        if response is not None:
            try:
                data = response.json().get("data") or {}
                cookies["buvid3"] = data.get("b_3") or cookies.get("buvid3", "")
                cookies["buvid4"] = data.get("b_4") or cookies.get("buvid4", "")
            except ValueError:
                pass

        cookie = "; ".join(f"{key}={value}" for key, value in sorted(cookies.items()) if value)
        # cache only complete jars: spi is the only reliable buvid4 source, and
        # caching an incomplete jar would persist the 412-prone fingerprint
        if cookie and cookies.get("buvid3") and cookies.get("buvid4"):
            self.headers["Cookie"] = cookie
            BilibiliUploaderChecker._cookie_cache = {"cookie": cookie, "ts": time.time()}
        elif cookie:
            self.headers["Cookie"] = cookie

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
            # empty hit_columns = keyword matched no field: bilibili pads the
            # tail of results with fuzzy "related" filler whose ranking drifts
            # in and out of the top pages between runs -> false update spikes
            if not item.get("hit_columns"):
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
            self._known_pubdates.setdefault(chapter_url, item.get("pubdate") or 0)

        return chapters

    def get_latest_chapter_list(self) -> List[Chapter] | None:
        """Get latest chapter list from Bilibili search API."""
        info = self._extract_info(self.check_url)
        if info is None:
            return []

        mid, keyword = info
        try:
            # inside the try: home/spi cookie fetches also 412 when the IP is flagged
            self._sync_bilibili_cookies()
            chapters = self._build_chapter_list(mid=mid, keyword=keyword)
        except requests.exceptions.RequestException as err:
            # HTTP 412 = bilibili flagged the egress IP (risk control); it
            # decays on its own — log one line instead of a traceback.
            logger.warning(
                "bilibili search blocked (IP risk control, retries later): %s (%s)",
                self.check_url,
                err,
            )
            # Signal a failed fetch: [] would read as a genuine empty list and
            # make the scheduler treat the producer as born empty, announcing
            # the whole shelf on the next success.
            return None

        # Bilibili search ranking drifts between runs, so an already-announced
        # video can leave and re-enter the top pages (bug: same update raised
        # twice). Keep seen chapters in the list forever; the URL-based diff in
        # the base checker then never re-reports them. New chapters keep their
        # pubdate order; dropped-but-recallable ones keep their remembered order.
        fresh_urls = {chapter.url for chapter in chapters}
        for chapter_url, chapter in self._known_chapters.items():
            if chapter_url not in fresh_urls:
                chapters.append(chapter)
        for chapter in chapters:
            self._known_chapters.setdefault(chapter.url, chapter)
        chapters.sort(key=lambda chapter: self._known_pubdates.get(chapter.url, 0))
        return chapters
