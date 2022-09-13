"""helpers for web scrapping"""
import logging
from typing import List
import chinese_converter
from helpers import checkers
from helpers.utils import get_main_domain_name, check_url_valid


CHECKER_DICT = {
    "wutuxs": checkers.WutuxsChecker,
    "syosetu": checkers.SyosetuChecker,
    "99wx": checkers.WxChecker,
    "manhuagui": checkers.ManhuaguiChecker,
    "qiman57": checkers.QimanChecker,
    "baozimh": checkers.BaozimhChecker,
    "xbiquge": checkers.XbiqugeChecker,
    "dashuhuwai": checkers.DashuhuwaiChecker,
}


class ChapterHelper:
    """Abstract helper class"""

    def __init__(
        self, name: str, urls: List, media_type: str, logger_name="dev"
    ) -> None:
        self.logger = logging.getLogger(logger_name)

        self.name = name
        self.urls = urls

        # Check if first url is valid, if not, use the next one
        for url in self.urls:
            if check_url_valid(url):
                self.check_url = url
                break
        else:
            # Use the first url if all urls are invalid
            self.check_url = self.urls[0]
        self.main_domain_name = get_main_domain_name(self.check_url)
        self.checker = None
        self.media_type = media_type

        # Set checker and media_type
        self.set_checker()

    def set_checker(self) -> None:
        """Initialize checker by checking keyword in check_url"""

        # Check if domain name is in checker_dict
        if self.main_domain_name in CHECKER_DICT:
            self.checker = CHECKER_DICT[self.main_domain_name](
                check_url=self.check_url
            )
        else:
            raise ValueError(
                f"Website {self.main_domain_name} is not supported yet."
            )

    def get_msg_content(self) -> str:
        """Construct html message content from helper and urls

        Returns:
            str: message content (html)
        """

        content_html_text = f"{self.name} {self.media_type} updated!\n"
        urls_texts = [
            f"<a href='{url}'>{self.main_domain_name}</a>" for url in self.urls
        ]
        content_html_text += " | ".join(urls_texts) + "\n"

        updated_chapter_list = self.checker.updated_chapter_list
        content_html_text += (
            f"Updated {len(updated_chapter_list)} chapter(s): "
        )
        chapter_texts = [
            f"<a href='{updated_chapter.url}'>{updated_chapter.title}</a>"
            for updated_chapter in updated_chapter_list
        ]
        content_html_text += ", ".join(chapter_texts)

        return chinese_converter.to_traditional(content_html_text)
