import time
import requests
from bs4 import BeautifulSoup
from hanziconv import HanziConv
from utils import get_logger

BASE_URL = "https://m.manhuagui.com"
RETRY_INTERVAL = 60 * 5  # unit in second
MAX_RETRY_NUM = 5

logger = get_logger(__name__)


class ManhuaguiHelper:
    def __init__(self, name, url) -> None:
        self.media_type = "comic"
        self.name = name
        self.url = url
        self.code = url.rsplit("/")[-2]
        self.a_link = f"/comic/{self.code}/"
        self.chapter_count = 0
        self.latest_chapter_url, self.latest_chapter_title = None, None
        (
            self.latest_chapter_url,
            self.latest_chapter_title,
        ) = self.get_latest_chapter()
        if self.latest_chapter_title is not None:
            self.latest_chapter_title_cht = HanziConv.toTraditional(
                self.latest_chapter_title
            )
        else:
            self.latest_chapter_title_cht = None

    def get_latest_chapter(self):
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
            except Exception as e:
                time.sleep(RETRY_INTERVAL)
            retry_num += 1
            # break and return current chapter if reach MAX_RETRY_NUM
            if retry_num >= MAX_RETRY_NUM:
                logger.warn(f"Reach max retry num for {self.url}")
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

        if len(chapter_list) > 0:
            # Get latest content
            latest_chapter_url, latest_chapter_title = chapter_list[0]
            latest_chapter_url = BASE_URL + latest_chapter_url
            return latest_chapter_url, latest_chapter_title
        else:
            logger.warn(f"Empty chapter list for {self.name} ({self.url})")
            return self.latest_chapter_url, self.latest_chapter_title

    def check_update(self):
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
        return BASE_URL in url


def test():
    name = "獨自一人的異世界攻略"
    url = "https://m.manhuagui.com/comic/30903/"
    manhuagui_helper = ManhuaguiHelper(name, url)
    url, title = manhuagui_helper.get_latest_chapter()
    print(title, url)


if __name__ == "__main__":
    test()
