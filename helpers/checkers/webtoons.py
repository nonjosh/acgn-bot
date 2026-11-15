"""Checker for webtoons.com comic list pages."""

from helpers.chapter import Chapter
from helpers.checkers.base import AbstractChapterChecker
from helpers.utils import get_logger

logger = get_logger(__name__)


class WebtoonsChecker(AbstractChapterChecker):
    """Webtoons checker

    Expects an episode list page URL like:
        https://www.webtoons.com/<lang>/<genre>/<slug>/list?title_no=<id>
    """

    URL_SUBSTRING = "webtoons.com"

    def get_latest_chapter_list(self) -> list[Chapter] | None:
        """Get latest chapter list from webtoons.com

        Returns:
            list[Chapter] | None: latest chapter list, or None when the page
                did not contain an episode list (fetch failure)
        """
        soup = self.get_latest_soup(apparent_encoding=False)
        if soup is None:
            return None

        # Episode items live in ul#_listUl as li._episodeItem, each holding an
        # a.detail_list_link; the readable title is in span.subj > span.
        #
        # A 200 page without that list (region block, maintenance page, markup
        # change) must not read as "series has no episodes": the scheduler
        # would mark it observed_empty and announce the whole list next time.
        container = soup.find(id="_listUl")
        if container is None:
            logger.warning("webtoons: no episode list at %s", self.check_url)
            return None

        chapter_list = []
        for li in container.find_all("li", class_="_episodeItem"):
            a_tag = li.find("a", href=True)
            if a_tag is None:
                continue
            span = a_tag.select_one("span.subj > span")
            title = (
                span.get_text(strip=True)
                if span
                else li.get("id", "").replace("episode_", "Chapter ")
            )
            chapter_list.append(Chapter(title=title, url=a_tag["href"]))

        # shortcut: only the first page (~10 newest episodes) is returned, so
        # >10 episodes released between two checks report only the newest page,
        # and the /latest chapter count caps at that page size. Paginate if
        # either ever matters.
        return chapter_list[::-1]
