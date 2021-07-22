import requests
import time
from bs4 import BeautifulSoup
from hanziconv import HanziConv

RETRY_INTERVAL = 60 * 5  # unit in second
MAX_RETRY_NUM = 5
BASE_URL = "https://ncode.syosetu.com"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36"
}


class Chapter:
    def __init__(self, title, url) -> None:
        self.title = title
        self.url = url

    def __repr__(self):
        return repr((self.url, self.title))


class SyosetuHelper:
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
        retry_num = 0

        while not request_sucess:
            try:
                # Connect to the URL
                response = requests.get(self.url, headers=HEADERS)
                if response.status_code == 200:
                    request_sucess = True
                else:
                    time.sleep(RETRY_INTERVAL)
            except Exception:
                time.sleep(RETRY_INTERVAL)
            retry_num += 1
            # break and return current chapter if reach MAX_RETRY_NUM
            if retry_num >= MAX_RETRY_NUM:
                return self.latest_chapter_url, self.latest_chapter_title

        soup = BeautifulSoup(response.text, "html.parser")

        chapterList = []
        for chapter_a in soup.find("div", {"class": "index_box"}).findAll("a"):
            title = chapter_a.text
            url = BASE_URL + chapter_a["href"]
            chapter = Chapter(title=title, url=url)
            chapterList.append(chapter)

        chapterListOrdered = sorted(
            chapterList, key=lambda item: (len(item.url), item.url)
        )

        try:
            # Get latest content
            latest_chapter_url, latest_chapter_title = (
                chapterListOrdered[-1].url,
                chapterListOrdered[-1].title,
            )
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


if __name__ == "__main__":
    syosetuHelper = SyosetuHelper("舔狗生肉", url="https://ncode.syosetu.com/n6621fl")

    print(syosetuHelper.getLatestChapter())
    # TODO use 真白萌 instead?
    # https://masiro.moe/forum.php?mod=viewthread&tid=38246&extra=page%3D1&page=1

    # request_sucess = False
    # RETRY_INTERVAL = 60 * 5  # unit in second
    # MAX_RETRY_NUM = 5
    # RETRY_NUM = 0

    # url = "https://ncode.syosetu.com/n6621fl"
    # headers = {
    #     "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36"
    # }

    # while not request_sucess:
    #     try:
    #         # Connect to the URL
    #         response = requests.get(url, headers=headers)
    #         if response.status_code == 200:
    #             request_sucess = True
    #         else:
    #             time.sleep(RETRY_INTERVAL)
    #     except Exception:
    #         time.sleep(RETRY_INTERVAL)
    #     RETRY_NUM += 1
    #     # break and return current chapter if reach MAX_RETRY_NUM
    #     if RETRY_NUM >= MAX_RETRY_NUM:
    #         print("fail to request url")

    # soup = BeautifulSoup(response.text, "html.parser")

    # chapterList = []
    # for chapter_a in soup.find("div", {"class": "index_box"}).findAll("a"):
    #     title = chapter_a.text
    #     url = BASE_URL + chapter_a["href"]
    #     chapter = Chapter(title=title, url=url)
    #     chapterList.append(chapter)
    #     # print(chapter)

    # for chapter in sorted(chapterList, key=lambda item: (len(item.url), item.url)):
    #     print(chapter)
