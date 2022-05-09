"""qiman6Helper"""
import logging
import time
import requests
from bs4 import BeautifulSoup
from hanziconv import HanziConv

BASE_URL = "https://www.baozimh.com"
RETRY_INTERVAL = 60 * 5  # unit in second
MAX_RETRY_NUM = 5


class BaozimhHelper:
    """BaozimhHelper"""

    def __init__(self, name, url, logger_name="dev") -> None:
        self.logger = logging.getLogger(logger_name)

        self.media_type = "comic"
        self.name = name
        self.url = url
        self.chapter_count = 0
        self.latest_chapter_url = self.latest_chapter_title = None
        (
            self.latest_chapter_url,
            self.latest_chapter_title,
        ) = self.get_latest_chapter()
        self.latest_chapter_title_cht = (
            HanziConv.toTraditional(self.latest_chapter_title)
            if self.latest_chapter_title is not None
            else None
        )

    def get_latest_chapter(self):
        """Get latest chapter

        Returns:
            tuple: (url, title)
        """
        request_sucess = False
        retry_num = 0

        while not request_sucess:
            try:
                # Connect to the URL
                response = requests.get(self.url)
                if response.status_code == 200:
                    request_sucess = True
                else:
                    time.sleep(RETRY_INTERVAL)
            except requests.exceptions.RequestException:
                time.sleep(RETRY_INTERVAL)
            retry_num += 1
            # break and return current chapter if reach MAX_RETRY_NUM
            if retry_num >= MAX_RETRY_NUM:
                self.logger.warning("Reach max retry number for %s", self.url)
                return self.latest_chapter_url, self.latest_chapter_title

        soup = BeautifulSoup(response.text, "html.parser")

        chapter_list = []
        a_list = [
            a.findAll("a", {"class": "comics-chapters__item"})[0]
            for a in soup.findAll("div", {"class": "pure-g"})[1]
        ]
        for chapter_item in a_list:
            title = chapter_item.text
            url = BASE_URL + chapter_item["href"]
            chapter = (url, title)
            chapter_list.append(chapter)

        chapter_list_ordered = chapter_list[::-1]

        if len(chapter_list_ordered) > 0:
            # Get latest content
            latest_chapter_obj = chapter_list_ordered[-1]
            return latest_chapter_obj

        self.logger.warning(
            "Empty chapter list for %s (%s)", self.name, self.url
        )
        return self.latest_chapter_url, self.latest_chapter_title

    def check_update(self):
        """Check update

        Returns:
            bool: True if update, False if not
        """
        _, latest_chapter_title = self.get_latest_chapter()

        if latest_chapter_title != self.latest_chapter_title:
            (
                self.latest_chapter_url,
                self.latest_chapter_title,
            ) = self.get_latest_chapter()
            self.latest_chapter_title_cht = HanziConv.toTraditional(
                self.latest_chapter_title
            )
            return True
        return False

    @staticmethod
    def match(url):
        """Match url

        Args:
            url (str): url to check

        Returns:
            bool: True if match, False if not
        """
        return BASE_URL in url
