"""helpers for web scrapping"""
import logging
from typing import List
from abc import ABC, abstractmethod
import chinese_converter
from helpers import checkers
from helpers.utils import get_main_domain_name, check_url_valid


class AbstractChapterHelper(ABC):
    """Abstract helper class"""

    def __init__(self, name: str, urls: List, logger_name="dev") -> None:
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
        self.media_type = None

        # Set checker and media_type
        self.set_checker()

    @abstractmethod
    def set_checker(self) -> None:
        """set checker and media_type"""
        raise NotImplementedError

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


class NovelChapterHelper(AbstractChapterHelper):
    """Novel helper class"""

    def set_checker(self) -> None:
        """Initialize checker"""

        checker_dict = {
            "wutuxs": checkers.WutuxsChecker(check_url=self.check_url),
            "syosetu": checkers.SyosetuChecker(check_url=self.check_url),
            "99wx": checkers.WxChecker(check_url=self.check_url),
        }
        # Check if domain name is in checker_dict
        if self.main_domain_name in checker_dict:
            self.checker = checker_dict[self.main_domain_name]
            self.media_type = "novel"
        else:
            raise ValueError(
                f"Website {self.main_domain_name} is not supported yet."
            )


class ComicChapterHelper(AbstractChapterHelper):
    """Comic helper class"""

    def set_checker(self) -> None:
        """Initialize checker"""

        checker_dict = {
            "manhuagui": checkers.ManhuaguiChecker(check_url=self.check_url),
            "qiman57": checkers.QimanChecker(check_url=self.check_url),
            "baozimh": checkers.BaozimhChecker(check_url=self.check_url),
            "xbiquge": checkers.XbiqugeChecker(check_url=self.check_url),
            "dashuhuwai": checkers.DashuhuwaiChecker(check_url=self.check_url),
        }
        # Check if domain name is in checker_dict
        if self.main_domain_name in checker_dict:
            self.checker = checker_dict[self.main_domain_name]
            self.media_type = "comic"
        else:
            raise ValueError(
                f"Website {self.main_domain_name} is not supported yet."
            )
