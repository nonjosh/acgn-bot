"""WutuxsHelper"""
import time
import requests
from bs4 import BeautifulSoup
import chinese_converter

BASE_URL = "http://www.wutuxs.com"
RETRY_INTERVAL = 60 * 5  # unit in second
MAX_RETRY_NUM = 5


class WutuxsHelper:
    """WutuxsHelper"""

    def __init__(self, name, url) -> None:
        self.media_type = "novel"
        self.name = name
        self.url = url
        self.a_link = url.replace(BASE_URL, "")
        self.chapter_count = 0
        (
            self.latest_chapter_url,
            self.latest_chapter_title,
        ) = self.get_latest_chapter()
        self.latest_chapter_title_cht = chinese_converter.to_traditional(
            self.latest_chapter_title
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
                    response.encoding = "gb18030"
                    request_sucess = True
                else:
                    time.sleep(RETRY_INTERVAL)
            except requests.exceptions.RequestException:
                time.sleep(RETRY_INTERVAL)
            retry_num += 1
            # break and return current chapter if reach MAX_RETRY_NUM
            if retry_num >= MAX_RETRY_NUM:
                return self.latest_chapter_url, self.latest_chapter_title

        soup = BeautifulSoup(response.text, "html.parser")

        a_tags = soup.findAll("a")

        chapter_list = []
        for i in range(0, len(a_tags) - 1):  # 'a' tags are for links
            one_a_tag = a_tags[i]

            try:
                link = one_a_tag["href"]
                if link.startswith(self.a_link):
                    chapter_title = one_a_tag.string
                    chapter_list.append((link, chapter_title))
            except KeyError:
                pass

        self.chapter_count = len(chapter_list)

        if len(chapter_list) > 0:
            # Get latest content
            latest_chapter_url, latest_chapter_title = chapter_list[-1]
            latest_chapter_url = BASE_URL + latest_chapter_url

            return latest_chapter_url, latest_chapter_title
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
            self.latest_chapter_title_cht = chinese_converter.to_traditional(
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
        return "http://www.wutuxs.com" in url
