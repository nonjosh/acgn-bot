import requests
from bs4 import BeautifulSoup
from hanziconv import HanziConv
from helpers.functions import *

BASE_URL = "https://www.cocomanhua.com"


class CocomanhuaHelper:
    def __init__(self, name, url) -> None:
        self.name = name
        self.url = url
        self.code = url.rsplit("/")[-2]
        self.a_link = f"/{self.code}/"
        self.chapter_count = 0
        self.latest_chapter_url, self.latest_chapter_title = self.getLatestChapter()
        printT(
            f"Current chapter for {self.name}: {self.latest_chapter_title} ({self.latest_chapter_url})"
        )
        pass

    def getLatestChapter(self):

        # Connect to the URL
        response = requests.get(self.url)

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

        try:
            # Get latest content
            latest_chapter_url, latest_chapter_title = chapter_list[0]
            latest_chapter_url = BASE_URL + latest_chapter_url

            return latest_chapter_url, latest_chapter_title
        except:
            return None, None

    def checkUpdate(self):
        _, latest_chapter_title = self.getLatestChapter()

        if latest_chapter_title != self.latest_chapter_title:
            self.latest_chapter_url, self.latest_chapter_title = self.getLatestChapter()
            return True
        else:
            return False


if __name__ == "__main__":
    cocomanhuaHelper1 = CocomanhuaHelper(
        name="萬古神王", url="https://www.cocomanhua.com/12970/"
    )

    print(cocomanhuaHelper1.getLatestChapter())
    print(cocomanhuaHelper1.name, cocomanhuaHelper1.latest_chapter_url)