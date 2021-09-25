import requests
import time
from bs4 import BeautifulSoup
from hanziconv import HanziConv

BASE_URL = "http://qiman6.com"


class Chapter:
    def __init__(self, title, url) -> None:
        self.title = title
        self.url = url

    def __repr__(self):
        return repr((self.url, self.title))


class Qiman6Helper:
    def __init__(self, name, url) -> None:
        self.name = name
        self.url = url
        self.code = url.rsplit("/")[-2]
        self.a_link = f"/comic/{self.code}/"
        self.chapter_count = 0
        self.latest_chapter_url, self.latest_chapter_title = None, None
        self.latest_chapter_url, self.latest_chapter_title = self.getLatestChapter()
        self.latest_chapter_title_cht = (
            HanziConv.toTraditional(self.latest_chapter_title)
            if self.latest_chapter_title is not None
            else None
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
        for chapterItem in soup.findAll("li", {"class": "chapter-item"}):
            title = chapterItem.find("a").text
            url = BASE_URL + chapterItem.find("a")["href"]
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
    name = "仙帝歸来"
    url = "http://qiman6.com/12235/"
    qiman6Helper = Qiman6Helper(name, url)
    url, title = qiman6Helper.getLatestChapter()
    print(title, url)
