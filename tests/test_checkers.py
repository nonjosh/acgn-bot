"""Test webscrapping function of the checker classes,
will skip if the url is not available."""

import unittest
from typing import List, Type

from helpers import checkers
from helpers.chapter import Chapter
from helpers.checkers import AbstractChapterChecker
from helpers.utils import check_url_valid


class TestCheckers(unittest.TestCase):
    """Check if can get chapter list for each Checker"""

    def validate_chapter_list(self, chapter_list: List[Chapter]) -> None:
        """Validate chapter list"""
        # Check if the list item is an Chapter object
        self.assertIsInstance(chapter_list[0], Chapter)

        # Check if the chapter list is not empty
        self.assertGreater(len(chapter_list), 0)

    def universal_checking(
        self, test_checker: Type[AbstractChapterChecker], check_url: str
    ) -> None:
        """Universal checker"""
        # Pass if the website is not healthy
        if not check_url_valid(url=check_url, verbose=True):
            self.skipTest(f"{check_url} is not healthy")
        # Initialize checker
        _checker = test_checker(check_url)

        # Check if can get chapter list
        chapter_list = _checker.get_latest_chapter_list()
        if len(chapter_list) == 0:
            self.skipTest(f"{check_url} is not healthy")
        self.validate_chapter_list(chapter_list)

    # Novel Checkers
    def test_syosetu_checker(self) -> None:
        """Syosetu"""
        self.universal_checking(
            test_checker=checkers.SyosetuChecker,
            check_url="https://ncode.syosetu.com/n6621fl/?p=2",
        )

    def test_piaotian_checker(self) -> None:
        """Piaotian"""
        self.universal_checking(
            test_checker=checkers.PiaotianChecker,
            check_url="https://www.piaotia.com/html/14/14565/",
        )

    # FIXME: Need JS cookies but postman can access?
    def test_wx_checker(self) -> None:
        """99wx"""
        self.universal_checking(
            test_checker=checkers.WxChecker,
            check_url="https://www.99wx.cc/wanxiangzhiwang/",
        )

    def test_69shuba_checker(self) -> None:
        """69shu"""
        self.universal_checking(
            test_checker=checkers.SixNineShuBaChecker,
            check_url="https://www.69shuba.com/book/43616.htm",
        )

    def test_linovelib_checker(self) -> None:
        """linovelib"""
        self.universal_checking(
            test_checker=checkers.LinovelibChecker,
            check_url="https://tw.linovelib.com/novel/3921/catalog",
        )

    # Comic Checkers
    def test_manhuagui_checker(self) -> None:
        """Manhuagui"""
        self.universal_checking(
            test_checker=checkers.ManhuaguiChecker,
            check_url="https://m.manhuagui.com/comic/17165/",
        )

    def test_qiman_checker(self) -> None:
        """Qiman"""
        self.universal_checking(
            test_checker=checkers.QimanChecker,
            check_url="http://qmanwu2.com/19827/",
        )

    def test_baozimh_checker(self) -> None:
        """Baozimh"""
        self.universal_checking(
            test_checker=checkers.BaozimhChecker,
            check_url="https://www.baozimh.com/comic/fangkainagenuwu-yuewenmanhua_e",
        )

    def test_baozimh2_checker(self) -> None:
        """another Baozimh"""
        self.universal_checking(
            test_checker=checkers.Baozimh2Checker,
            check_url="https://baozimh.org/manga/xiaoshimeimingmingchaoqiangqueguofenshadiao",
        )

    def test_biqu_checker(self) -> None:
        """Biqu"""
        self.universal_checking(
            test_checker=checkers.BiquChecker,
            check_url="http://m.biqu520.net/wapbook-147321/",
        )

    def test_xbiquge_checker(self) -> None:
        """Xbiquge"""
        self.universal_checking(
            test_checker=checkers.XbiqugeChecker,
            check_url="https://www.xbiquge.bz/book/53099/",
        )

    # FIXME: Need JS cookies but postman can access?
    def test_dashumanhua_checker(self) -> None:
        """Dashumanhua"""
        self.universal_checking(
            test_checker=checkers.DashumanhuaChecker,
            check_url="https://www.dashumanhua.com/comic/fangkainagenvwu/",
        )

    def test_mn4u_checker(self) -> None:
        """Mn4u"""
        self.universal_checking(
            test_checker=checkers.Mn4uChecker,
            check_url="https://mn4u.net/zgm-2149/",
        )

    @unittest.skip("mangakl website is no longer available")
    def test_klmanga_checker(self) -> None:
        """Klmanga"""
        self.universal_checking(
            test_checker=checkers.KlmanagaChecker,
            check_url="https://mangakl.su/tensei-shitara-dai-nana-ouji-dattanode-kimamani-majutsu-o-kiwamemasu-raw",
        )

    def test_kunmanga_checker(self) -> None:
        """Kunmanga"""
        self.universal_checking(
            test_checker=checkers.KunmangaChecker,
            check_url="https://kunmanga.com/manga/sss-class-suicide-hunter/",
        )

    def test_jmanga_checker(self) -> None:
        """jmanga"""
        self.universal_checking(
            test_checker=checkers.JmangaChecker,
            check_url="https://jmanga.so/read/%E3%83%A4%E3%83%B3%E3%83%87%E3%83%AC%E9%AD%94%E6%B3%95%E4%BD%BF%E3%81%84%E3%81%AF%E7%9F%B3%E5%83%8F%E3%81%AE%E4%B9%99%E5%A5%B3%E3%81%97%E3%81%8B%E6%84%9B%E3%81%9B%E3%81%AA%E3%81%84-%E9%AD%94%E5%A5%B3%E3%81%AF%E6%84%9B%E5%BC%9F%E5%AD%90%E3%81%AE%E7%86%B1%E3%81%84%E5%8F%A3%E3%81%A5%E3%81%91%E3%81%A7%E3%81%A8%E3%81%91%E3%82%8B-raw/",
        )

    def test_weixin_checker(self) -> None:
        """Weixin"""
        self.universal_checking(
            test_checker=checkers.WeixinChecker,
            check_url="https://mp.weixin.qq.com/mp/appmsgalbum?action=getalbum&album_id=2989381295912878080",
        )

    def test_laimanhua_checker(self) -> None:
        """Laimanhua"""
        self.universal_checking(
            test_checker=checkers.LaimanhuaChecker,
            check_url="https://www.laimanhua88.com/kanmanhua/quanzhiduzheshijiao/",
        )
