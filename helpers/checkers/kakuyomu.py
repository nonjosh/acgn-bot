from typing import List, Optional
from urllib.parse import urlparse, urlunparse

from bs4 import BeautifulSoup
from bs4.element import Tag

from helpers.chapter import Chapter
from helpers.checkers.base import AbstractChapterChecker


class KakuyomuChecker(AbstractChapterChecker):
    """Kakuyomu checker.

    Supports parsing both:
    - Work page: https://kakuyomu.jp/works/<work_id>
    - Episode page: https://kakuyomu.jp/works/<work_id>/episodes/<episode_id>
    - Episode sidebar: .../episode_sidebar (preferred because it contains a compact TOC)
    """

    URL_SUBSTRING = "kakuyomu.jp"

    def _make_absolute_url(self, href: str) -> str:
        if not href:
            return self.check_url
        if href.startswith("http://") or href.startswith("https://"):
            return href
        parsed = urlparse(self.check_url)
        return urlunparse(parsed._replace(path=href, params="", query="", fragment=""))

    def _get_toc_url(self) -> str:
        """Prefer the episode sidebar when the input URL is an episode URL."""
        parsed = urlparse(self.check_url)
        path = (parsed.path or "/").rstrip("/")

        # Already an episode sidebar URL.
        if path.endswith("/episode_sidebar"):
            return urlunparse(parsed._replace(params="", query="", fragment=""))

        # Episode page URL -> use its sidebar (more reliable for TOC extraction).
        if "/episodes/" in path:
            sidebar_path = f"{path}/episode_sidebar"
            return urlunparse(
                parsed._replace(path=sidebar_path, params="", query="", fragment="")
            )

        # Work URL (or something else) -> try parsing as-is.
        return urlunparse(parsed._replace(params="", query="", fragment=""))

    def _extract_chapter_list_from_soup(self, soup: BeautifulSoup) -> List[Chapter]:
        chapter_list: List[Chapter] = []

        # Kakuyomu TOC items look like:
        # <ol class="widget-toc-items"> <li class="widget-toc-episode"> <a class="widget-toc-episode-episodeTitle" href="...">
        a_tags = soup.select(
            "ol.widget-toc-items li.widget-toc-episode a.widget-toc-episode-episodeTitle"
        )
        if not a_tags:
            # Fallback: sometimes the list may be present without the ol class.
            a_tags = soup.select("a.widget-toc-episode-episodeTitle")

        for a_tag in a_tags:
            if not isinstance(a_tag, Tag):
                continue

            href = a_tag.get("href", "")
            url = self._make_absolute_url(href)

            title_tag: Optional[Tag] = a_tag.select_one(
                ".widget-toc-episode-titleLabel"
            )
            title = (
                title_tag.get_text(strip=True)
                if title_tag
                else a_tag.get_text(" ", strip=True)
            )
            # Kakuyomu commonly uses the ideographic space (U+3000) between
            # episode number and title; normalize it for consistent diffs/alerts.
            title = title.replace("\u3000", " ").strip()
            if not title or not href:
                continue

            chapter_list.append(Chapter(title=title, url=url))

        return chapter_list

    def get_latest_chapter_list(self) -> List[Chapter]:
        toc_url = self._get_toc_url()
        response = self.get_latest_response(url=toc_url)
        if response is None:
            return []

        soup = BeautifulSoup(response.text, "html.parser")
        return self._extract_chapter_list_from_soup(soup)
