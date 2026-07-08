"""Checker for Mangakatana manga pages."""

from typing import override
from urllib.parse import urlparse

from helpers.chapter import Chapter
from helpers.checkers.base import AbstractChapterChecker


class MangakatanaChecker(AbstractChapterChecker):
    """Mangakatana chapter list checker."""

    URL_SUBSTRING: str = "mangakatana.com/manga/"

    @override
    def get_latest_chapter_list(self) -> list[Chapter]:
        """Get latest chapter list from Mangakatana.

        Returns:
            list[Chapter]: latest chapter list ordered from oldest to newest
        """
        soup = self.get_latest_soup(apparent_encoding=False)
        if not soup:
            return []

        parsed_url = urlparse(self.check_url)
        comic_path = parsed_url.path.rstrip("/")
        chapter_table = soup.select_one("div.chapters table")
        if chapter_table is None:
            return []

        chapter_list: list[Chapter] = []
        for a_tag in chapter_table.select("div.chapter a[href]"):
            href = a_tag.get("href")
            if not isinstance(href, str):
                continue

            chapter_url = href.strip()
            chapter_path = urlparse(chapter_url).path.rstrip("/")
            if not chapter_path.startswith(f"{comic_path}/c"):
                continue

            chapter_title = a_tag.get_text(" ", strip=True)
            if not chapter_title:
                continue

            chapter_list.append(Chapter(title=chapter_title, url=chapter_url))

        return chapter_list[::-1]
