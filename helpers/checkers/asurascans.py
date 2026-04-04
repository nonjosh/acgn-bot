"""Checker for asurascans.com comic pages."""

from typing import List
from urllib.parse import urljoin

from helpers.chapter import Chapter
from helpers.checkers.base import AbstractChapterChecker


class AsurascansChecker(AbstractChapterChecker):
    """Asurascans checker

    Expects a comic page URL like:
        https://asurascans.com/comics/<slug>
    """

    URL_SUBSTRING = "asurascans.com"

    def get_latest_chapter_list(self) -> List[Chapter]:
        """Get latest chapter list from asurascans.com

        Returns:
            List[Chapter]: latest chapter list
        """
        soup = self.get_latest_soup(apparent_encoding=False)
        if soup is None:
            return []

        # Chapter links live inside a scrollable div (max-h-[500px] overflow-y-auto)
        # containing a child div with class "divide-y divide-white/5".
        # Each <a> inside that div links to /comics/<slug>/chapter/<num>.
        container = soup.find("div", class_="overflow-y-auto")
        if container is None:
            return []

        chapter_list = []
        for a_tag in container.find_all("a", href=True):
            href = a_tag["href"]
            if "/chapter/" not in href:
                continue

            # Build chapter title from the span text
            span = a_tag.find("span", class_=lambda c: c and "font-medium" in c)
            title = (
                span.get_text(" ", strip=True)
                if span
                else a_tag.get_text(" ", strip=True)
            )

            url = urljoin(self.check_url, href)
            chapter_list.append(Chapter(title=title, url=url))

        # Chapters are listed newest-first on the page; reverse to oldest-first
        return chapter_list[::-1]
