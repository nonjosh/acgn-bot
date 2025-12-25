from typing import List
from urllib.parse import urljoin, urlparse

from bs4 import BeautifulSoup

from helpers.chapter import Chapter
from helpers.checkers.base import AbstractChapterChecker


class PickmeupgachaChecker(AbstractChapterChecker):
    """Simple checker for pickmeupgacha site"""

    URL_SUBSTRING = "pickmeupgacha"

    def get_latest_chapter_list(self) -> List[Chapter]:
        """Get latest chapter list by extracting meaningful links from page"""
        soup: BeautifulSoup = self.get_latest_soup()
        if not soup:
            return []

        # Only consider links within <h3 class="elementor-post__title"> blocks
        title_blocks = soup.find_all("h3", class_="elementor-post__title")

        chapter_list: List[Chapter] = []
        for block in title_blocks:
            a = block.find("a", href=True)
            if a is None:
                continue

            title = a.get_text().strip()
            if not title:
                continue

            href = a["href"]
            # Build absolute URL
            if href.startswith("http"):
                url = href
            else:
                url = urljoin(self.check_url, href)

            # Only include links that point to the same site (avoid external links)
            try:
                netloc = urlparse(url).netloc
            except Exception:
                continue

            if "pickmeupgacha" not in netloc:
                continue

            chapter_list.append(Chapter(title=title, url=url))

        # Remove duplicates while preserving order
        seen = set()
        unique_list: List[Chapter] = []
        for ch in chapter_list:
            key = (ch.title, ch.url)
            if key in seen:
                continue
            seen.add(key)
            unique_list.append(ch)

        # Return in chronological order (oldest first)
        return unique_list[::-1]
