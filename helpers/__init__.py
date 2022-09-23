"""helpers for web scrapping"""
import logging
from typing import List, Literal
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
    "mn4u": checkers.Mn4uChecker,
    "comick": checkers.ComickChecker,
}

MediaTypes = Literal["novel", "comic"]


class ChapterHelper:
    """Abstract helper class"""

    def __init__(
        self,
        name: str,
        urls: List,
        media_type: MediaTypes,
        logger_name="dev",
    ) -> None:
        self.logger = logging.getLogger(logger_name)

        self.name = name
        self.urls = urls
        self.media_type = media_type
        assert self.media_type in ["novel", "comic"]

        self.checker = None

        # Set check_url, main_domain_name and checker
        # Check if first url is valid, if not, use the next one
        for url in self.urls:
            if check_url_valid(url):
                self.check_url = url
                self.main_domain_name = get_main_domain_name(self.check_url)
                # Set checker
                if self.set_checker():
                    # Escape for loop if checker is set successfully
                    break
        else:
            # Use the first url if all urls are invalid
            self.check_url = self.urls[0]

    def set_checker(self) -> bool:
        """Initialize checker by checking keyword in check_url

        Returns:
            bool: True if checker is set successfully
        """

        # Check if domain name is in checker_dict
        if self.main_domain_name in CHECKER_DICT:
            self.checker = CHECKER_DICT[self.main_domain_name](
                check_url=self.check_url
            )
            return True
        self.logger.error(
            "Domain name %s is not supported", self.main_domain_name
        )
        return False

    def get_urls_text(self) -> str:
        """Construct urls text from urls
            e.g. qiman57 | cocomanga

        Returns:
            str: urls text
        """
        urls_texts = [
            f"<a href='{url}'>{get_main_domain_name(url)}</a>"
            for url in self.urls
        ]
        return " | ".join(urls_texts) + "\n"

    def get_msg_content(self) -> str:
        """Construct html message content from helper and urls

        Returns:
            str: message content (html)
        """

        # 元尊 comic updated!
        content_html_text = f"{self.media_type} {self.name} updated!\n"

        # qiman57 | cocomanga
        content_html_text += self.get_urls_text()

        # Updated 3 chapter(s): 第六百二十六章 挑戰鐘太丘, 第六百二十七章 虛珠, 第六百二十八章 巔峰對決
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
