import requests
import time
from bs4 import BeautifulSoup
from hanziconv import HanziConv

BASE_URL = "https://m.manhuagui.com/"


class ManhuaguiHelper:
    def __init__(self, name, url) -> None:
        self.name = name
        self.url = url
        self.code = url.rsplit("/")[-2]
        self.a_link = f"/comic/{self.code}/"
        self.chapter_count = 0
        self.latest_chapter_url, self.latest_chapter_title = self.getLatestChapter()
        self.latest_chapter_title_cht = HanziConv.toTraditional(
            self.latest_chapter_title
        )
        pass

    def getLatestChapter(self):
        request_sucess = False
        RETRY_INTERVAL = 60 * 5  # unit in second
        MAX_RETRY_NUM = 5
        RETRY_NUM = 0

        while not request_sucess:
            try:
                # Connect to the URL
                response = requests.get(self.url)
                if response.status_code == 200:
                    request_sucess = True
                else:
                    time.sleep(RETRY_INTERVAL)
            except Exception:
                time.sleep(RETRY_INTERVAL)
            RETRY_NUM += 1
            # break and return current chapter if reach MAX_RETRY_NUM
            if RETRY_NUM >= MAX_RETRY_NUM:
                return self.latest_chapter_url, self.latest_chapter_title

        soup = BeautifulSoup(response.text, "html.parser")

        a_tags = soup.findAll("a")

        chapter_list = []
        for i in range(0, len(a_tags) - 1):  # 'a' tags are for links
            one_a_tag = a_tags[i]

            try:
                link = one_a_tag["href"]
                if link.startswith(self.a_link):
                    chapter_title = one_a_tag.text
                    chapter_list.append((link, chapter_title))
            except KeyError:
                pass

        self.chapter_count = len(chapter_list)

        try:
            # Get latest content
            latest_chapter_url, latest_chapter_title = chapter_list[0]
            latest_chapter_url = BASE_URL + latest_chapter_url

            return latest_chapter_url, latest_chapter_title
        except:
            return self.latest_chapter_url, self.latest_chapter_title

    def checkUpdate(self):
        _, latest_chapter_title = self.getLatestChapter()

        if latest_chapter_title != self.latest_chapter_title:
            self.latest_chapter_url, self.latest_chapter_title = self.getLatestChapter()
            self.latest_chapter_title_cht = HanziConv.toTraditional(
                self.latest_chapter_title
            )
            return True
        else:
            return False

    @staticmethod
    def match(url):
        return BASE_URL in url
