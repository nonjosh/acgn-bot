"""Checkers"""
from typing import List
import time
from urllib.parse import urlparse, urlunparse, urljoin
import json
from helpers.chapter import Chapter
from helpers.checkers.base import AbstractChapterChecker


class WxChecker(AbstractChapterChecker):
    """99wx checker class"""

    def get_latest_chapter_list(self) -> List[Chapter]:
        """Get latest chapter list

        Returns:
            List[Chapter]: latest chapter list
        """
        soup = self.get_latest_soup()
        if not soup:
            return []

        a_list = list(soup.find("div", id="play_0").findAll("a"))
        chapter_list = []
        for chapter_tag in a_list:
            chapter_title = chapter_tag.text
            chapter_path = chapter_tag["href"]
            chapter_url = urlunparse(
                urlparse(self.check_url)._replace(path=chapter_path)
            )
            chapter_list.append(Chapter(title=chapter_title, url=chapter_url))

        # Reverse chapter list if it is comic
        if "/manhua/" in self.check_url:
            chapter_list.reverse()
        return chapter_list


class SyosetuChecker(AbstractChapterChecker):
    """Syosetu checker class"""

    def get_latest_chapter_list(self) -> List[Chapter]:
        """Get latest chapter list

        Returns:
            List[Chapter]: latest chapter list
        """
        soup = self.get_latest_soup()
        if not soup:
            return []

        dl_list = list(soup.find("div", {"class": "index_box"}).findAll("a"))
        chapter_list = []
        for chapter_tag in dl_list:
            chapter_title = chapter_tag.text
            chapter_path = chapter_tag["href"]
            chapter_url = urlunparse(
                urlparse(self.check_url)._replace(path=chapter_path)
            )
            chapter_list.append(Chapter(title=chapter_title, url=chapter_url))

        return chapter_list


class PiaotianChecker(AbstractChapterChecker):
    """Piaotian novel checker class"""

    def get_latest_chapter_list(self) -> List[Chapter]:
        """Get latest chapter list

        Returns:
            List[Chapter]: latest chapter list
        """
        soup = self.get_latest_soup()
        if not soup:
            return []

        dl_list = list(soup.find("div", {"class": "centent"}).findAll("a"))
        chapter_list = []
        for chapter_tag in dl_list:
            chapter_title = chapter_tag.text
            chapter_path = chapter_tag["href"]
            chapter_url = urljoin(self.check_url, chapter_path)
            chapter_list.append(Chapter(title=chapter_title, url=chapter_url))

        return chapter_list


class SixNineShuBaChecker(AbstractChapterChecker):
    """69shu checker class"""

    def get_latest_chapter_list(self) -> List[Chapter]:
        """Get latest chapter list

        Returns:
            List[Chapter]: latest chapter list
        """
        soup = self.get_latest_soup()
        if not soup:
            return []

        dl_list = list(soup.find("div", {"class": "qustime"}).findAll("a"))
        chapter_list = []
        for chapter_tag in dl_list:
            chapter_title = chapter_tag.find("span").text
            chapter_url = chapter_tag["href"]
            chapter_list.append(Chapter(title=chapter_title, url=chapter_url))

        return chapter_list


class ManhuaguiChecker(AbstractChapterChecker):
    """Manhuagui chapter list"""

    def get_latest_chapter_list(self) -> List[Chapter]:
        """Get latest chapter list from manhuagui

        Returns:
            List[Chapter]: latest chapter list
        """
        soup = self.get_latest_soup()
        if not soup:
            return []

        comic_path = urlparse(self.check_url).path

        a_tags = soup.findAll("a")

        chapter_list = []
        for i in range(0, len(a_tags) - 1):  # 'a' tags are for links
            one_a_tag = a_tags[i]

            try:
                chapter_path = one_a_tag["href"]
                if chapter_path.startswith(comic_path):
                    chapter_title = one_a_tag.text
                    chapter_url = urlunparse(
                        urlparse(self.check_url)._replace(path=chapter_path)
                    )
                    chapter_list.append(Chapter(title=chapter_title, url=chapter_url))
            except KeyError:
                pass

        return chapter_list[::-1]


class QimanChecker(AbstractChapterChecker):
    """QimanChecker"""

    def get_latest_chapter_list(self) -> List[Chapter]:
        """Get latest chapter list from qiman

        Returns:
            List[Chapter]: latest chapter list
        """
        # Update last check time
        self.last_check_time = time.strftime("%Y-%m-%dT%H:%M:%S%z")

        # Construct api url
        url_parse = urlparse(self.check_url)
        api_url = urlunparse(url_parse._replace(path="/bookchapter/"))

        comic_id = int(urlparse(self.check_url).path.strip("/"))

        try:
            # Send with POST method
            response = self.get_lastest_post_response(
                url=api_url, data={"id": comic_id, "id2": 1}
            )
            """Sample response:
            [
                {
                    "id": "886859",
                    "name": "周刊136话"
                },
                {
                    "id": "886858",
                    "name": "周刊135话"
                },
                {
                    "id": "886857",
                    "name": "周刊134话"
                },
                ...
            ]
            """
            chapter_list = []
            for chapter_obj in response.json():
                chapter_id = chapter_obj["id"]
                chapter_url = urlunparse(
                    url_parse._replace(path=f"/{comic_id}/{chapter_id}.html")
                )
                chapter_list.append(Chapter(title=chapter_obj["name"], url=chapter_url))
            return chapter_list[::-1]
        except AttributeError:
            return []
        except json.decoder.JSONDecodeError:
            return []


class BaozimhChecker(AbstractChapterChecker):
    """Baozimh checker"""

    def get_latest_chapter_list(self) -> List[Chapter]:
        """Get latest chapter list from baozimh

        Returns:
            List[Chapter]: latest chapter list
        """
        soup = self.get_latest_soup(apparent_encoding=False)
        if soup is None:
            return []

        pure_g_div_list = soup.findAll("div", {"class": "pure-g"})

        # Find which div contains chapter items
        for pure_g_div in pure_g_div_list:
            if pure_g_div.find("a", {"class": "comics-chapters__item"}):
                a_list = [
                    a.findAll("a", {"class": "comics-chapters__item"})
                    for a in pure_g_div
                ]
                chapter_list = []
                for chapter_tag in a_list:
                    chapter_title = chapter_tag[0].text
                    chapter_path = chapter_tag[0]["href"]
                    chapter_url = urlunparse(
                        urlparse(self.check_url)._replace(path=chapter_path)
                    )
                    chapter_list.append(Chapter(title=chapter_title, url=chapter_url))

                return chapter_list[::-1]
        return []


class XbiqugeChecker(AbstractChapterChecker):
    """Xbiquge checker"""

    def get_latest_chapter_list(self) -> List[Chapter]:
        """Get latest chapter list from xbiquge

        Returns:
            List[Chapter]: latest chapter list
        """
        soup = self.get_latest_soup()
        if soup is None:
            return []
        a_list = list(soup.find("div", id="list").findAll("a"))
        chapter_list = []
        for chapter_tag in a_list:
            chapter_title = chapter_tag.text
            chapter_path = chapter_tag["href"]
            chapter_url = urljoin(self.check_url, chapter_path)
            chapter_list.append(Chapter(title=chapter_title, url=chapter_url))

        # Remvoe duplicated
        chapter_list = list(set(chapter_list))

        # Sort by chapter url
        chapter_list.sort(key=lambda x: x.url)
        return chapter_list


class DashuhuwaiChecker(AbstractChapterChecker):
    """Dashuhuwai checker"""

    def get_latest_chapter_list(self) -> List[Chapter]:
        """Get latest chapter list from dashuhuwai

        Returns:
            List[Chapter]: latest chapter list
        """
        soup = self.get_latest_soup()
        if soup is None:
            return []
        a_list = [li.find("a") for li in soup.find(id="ul_chapter1").find_all("li")]
        chapter_list = []
        for chapter_tag in a_list:
            chapter_title = chapter_tag.text
            chapter_path = chapter_tag["href"]
            chapter_url = urlunparse(
                urlparse(self.check_url)._replace(path=chapter_path)
            )
            chapter_list.append(Chapter(title=chapter_title, url=chapter_url))

        return chapter_list


class Mn4uChecker(AbstractChapterChecker):
    """Mn4u checker"""

    def __init__(self, check_url: str) -> None:
        super().__init__(check_url)
        self.headers["referer"] = self.check_url
        mid = urlparse(self.check_url).path.strip("/").split("-")[1]
        self.params = {"mid": mid}
        self.check_url = "https://mn4u.net/app/manga/controllers/cont.listChapter.php"

    def get_latest_chapter_list(self) -> List[Chapter]:
        """Get latest chapter list from mn4u

        Returns:
            List[Chapter]: latest chapter list
        """
        soup = self.get_latest_soup()
        if soup is None:
            return []
        a_list = list(soup.find("ul", {"class": "list-chapters"}).findAll("a"))
        chapter_list = []
        for chapter_tag in a_list:
            chapter_title = chapter_tag.find("div", {"class": "chapter-name"}).text
            chapter_path = chapter_tag["href"]
            chapter_url = urlunparse(
                urlparse(self.check_url)._replace(path=chapter_path)
            )
            chapter_list.append(Chapter(title=chapter_title, url=chapter_url))

        # Reverse the list to get the latest chapter first
        return chapter_list[::-1]


class KlmanagaChecker(AbstractChapterChecker):
    """Klmanaga checker"""

    def get_latest_chapter_list(self) -> List[Chapter]:
        """Get latest chapter list from klmanga

        Returns:
            List[Chapter]: latest chapter list
        """
        soup = self.get_latest_soup()
        if soup is None:
            return []
        a_list = list(soup.find("div", id="list-chapter").findAll("a"))
        chapter_list = []
        for chapter_tag in a_list:
            if chapter_tag.get("title"):
                chapter_title = chapter_tag["title"]
                chapter_path = chapter_tag["href"]
                chapter_url = urlunparse(
                    urlparse(self.check_url)._replace(path=chapter_path)
                )
                chapter_list.append(Chapter(title=chapter_title, url=chapter_url))

        # Reverse the list to get the latest chapter first
        return chapter_list[::-1]
