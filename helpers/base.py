"""Base helper class"""
import logging


class BaseHelper:
    """Base Helper"""

    def __init__(self, name, url, logger_name="dev") -> None:
        self.logger = logging.getLogger(logger_name)

        self.name = name
        self.url = url
        self.chapter_list = []
        self.latest_chapter_title_cht = None

    def __repr__(self):
        return repr((self.name, self.url, len(self.chapter_list)))
