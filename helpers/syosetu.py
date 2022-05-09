""" SyosetuHelper """
import time
import requests
from bs4 import BeautifulSoup
from hanziconv import HanziConv
from helpers.chapter import Chapter

RETRY_INTERVAL = 60 * 5  # unit in second
MAX_RETRY_NUM = 5
BASE_URL = "https://ncode.syosetu.com"
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36"
        " (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36"
    )
}


class SyosetuHelper:
    """SyosetuHelper"""

    def __init__(self, name, url, translate_url=None) -> None:
        self.media_type = "novel"
        self.name = name
        self.url = url
        self.code = url.rsplit("/")[-2]
        self.a_link = f"/comic/{self.code}/"
        self.translate_url = translate_url
        self.chapter_count = 0
        (
            self.latest_chapter_url,
            self.latest_chapter_title,
        ) = self.get_latest_chapter()
        self.latest_chapter_title_cht = HanziConv.toTraditional(
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
                response = requests.get(self.url, headers=HEADERS)
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
        for chapter_a in soup.find("div", {"class": "index_box"}).findAll("a"):
            title = chapter_a.text
            url = BASE_URL + chapter_a["href"]
            chapter = Chapter(title=title, url=url)
            chapter_list.append(chapter)

        chapter_list_ordered = sorted(
            chapter_list, key=lambda item: (len(item.url), item.url)
        )

        if len(chapter_list_ordered) > 0:
            # Get latest content
            latest_chapter_url, latest_chapter_title = (
                chapter_list_ordered[-1].url,
                chapter_list_ordered[-1].title,
            )
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


if __name__ == "__main__":
    syosetuHelper = SyosetuHelper(
        "舔狗生肉",
        url="https://ncode.syosetu.com/n6621fl",
        translate_url="https://masiro.me/admin/novelView?novel_id=212",
    )

    print(syosetuHelper.get_latest_chapter())

    # request_sucess = False
    # RETRY_INTERVAL = 60 * 5  # unit in second
    # MAX_RETRY_NUM = 5
    # RETRY_NUM = 0

    # url = "https://ncode.syosetu.com/n6621fl"
    # headers = {
    #     "User-Agent": (
    #         "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5)"
    #         " AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102"
    #         " Safari/537.36"
    #     )
    # }

    # while not request_sucess:
    #     try:
    #         # Connect to the URL
    #         response = requests.get(url, headers=headers)
    #         if response.status_code == 200:
    #             request_sucess = True
    #         else:
    #             time.sleep(RETRY_INTERVAL)
    #     except Exception as e:
    #         time.sleep(RETRY_INTERVAL)
    #     RETRY_NUM += 1
    #     # break and return current chapter if reach MAX_RETRY_NUM
    #     if RETRY_NUM >= MAX_RETRY_NUM:
    #         print("fail to request url")

    # soup = BeautifulSoup(response.text, "html.parser")

    # chapter_list = []
    # for chapter_a in soup.find("div", {"class": "index_box"}).findAll("a"):
    #     title = chapter_a.text
    #     url = BASE_URL + chapter_a["href"]
    #     chapter = Chapter(title=title, url=url)
    #     chapter_list.append(chapter)
    #     # print(chapter)

    # for chapter in sorted(chapter_list, key=lambda item: (len(item.url), item.url)):
    #     print(chapter)
