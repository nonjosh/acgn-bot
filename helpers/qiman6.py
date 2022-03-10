"""qiman6Helper"""
import time
import requests
from bs4 import BeautifulSoup
from hanziconv import HanziConv

BASE_URL = "http://qiman6.com"
RETRY_INTERVAL = 60 * 5  # unit in second
MAX_RETRY_NUM = 5


class Chapter:
    """Chapter class"""

    def __init__(self, title, url) -> None:
        self.title = title
        self.url = url

    def __repr__(self):
        return repr((self.url, self.title))


class Qiman6Helper:
    """Qiman6Helper"""

    def __init__(self, name, url) -> None:
        self.media_type = "comic"
        self.name = name
        self.url = url
        self.code = url.rsplit("/")[-2]
        self.a_link = f"/comic/{self.code}/"
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
                return self.latest_chapter_url, self.latest_chapter_title

        soup = BeautifulSoup(response.text, "html.parser")

        chapter_list = []
        for chapter_item in soup.findAll("li", {"class": "chapter-item"}):
            title = chapter_item.find("a").text
            url = BASE_URL + chapter_item.find("a")["href"]
            chapter = Chapter(title=title, url=url)
            chapter_list.append(chapter)

        chapter_list_ordered = sorted(
            chapter_list, key=lambda item: (len(item.url), item.url)
        )

        if len(chapter_list_ordered) > 0:
            # Get latest content
            latest_chapter_obj = chapter_list_ordered[-1]
            return latest_chapter_obj.url, latest_chapter_obj.title
        else:
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
        else:
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


def test():
    """test"""
    name = "仙帝歸来"
    url = "http://qiman6.com/12235/"
    qiman6_helper = Qiman6Helper(name, url)
    url, title = qiman6_helper.get_latest_chapter()
    print(title, url)


if __name__ == "__main__":
    test()
