import requests
import time
from bs4 import BeautifulSoup
from hanziconv import HanziConv


class Chapter:
    def __init__(self, title, url) -> None:
        self.title = title
        self.url = url

    def __repr__(self):
        return repr((self.url, self.title))


BASE_URL = "https://www.esjzone.cc/"


class EsjzoneHelper:
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

        chapterList = []
        for chapterDiv in soup.find("div", id="chapterList").findAll("a"):
            title = chapterDiv.text
            url = (
                chapterDiv["href"].replace("www.esjzone.cc", "esjzone.cc").split("#")[0]
            )
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
            latest_chapter_url = latest_chapter_url

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
    request_sucess = False
    RETRY_INTERVAL = 60 * 5  # unit in second
    MAX_RETRY_NUM = 5
    RETRY_NUM = 0

    url = "https://www.esjzone.cc/detail/1591099430.html"
    while not request_sucess:
        try:
            # Connect to the URL
            response = requests.get(url)
            if response.status_code == 200:
                request_sucess = True
            else:
                time.sleep(RETRY_INTERVAL)
        except Exception:
            time.sleep(RETRY_INTERVAL)
        RETRY_NUM += 1
        # break and return current chapter if reach MAX_RETRY_NUM
        if RETRY_NUM >= MAX_RETRY_NUM:
            print("fail to request url")

    soup = BeautifulSoup(response.text, "html.parser")

    chapterList = []
    for chapterDiv in soup.find("div", id="chapterList").findAll("a"):
        title = chapterDiv.text
        url = chapterDiv["href"].replace("www.esjzone.cc", "esjzone.cc").split("#")[0]
        chapter = Chapter(title=title, url=url)
        chapterList.append(chapter)
        # print(chapter)

    for chapter in sorted(chapterList, key=lambda item: (len(item.url), item.url)):
        print(chapter)
