"""Test webscrapping function of the checker classes,
will skip if the url is not available."""
import unittest
from helpers.chapter import Chapter
from helpers import checkers
from helpers.utils import check_url_valid


class TestCheckers(unittest.TestCase):
    """Check if can get chapter list for each Checker"""

    def validate_chapter_list(self, chapter_list: list):
        """Validate chapter list"""
        # Check if the list item is an Chapter object
        self.assertIsInstance(chapter_list[0], Chapter)

        # Check if the chapter list is not empty
        self.assertGreater(len(chapter_list), 0)

    def universal_checking(self, test_checker, check_url: str):
        """Universal checker"""
        # Pass if the website is not healthy
        if check_url_valid(url=check_url, verbose=True):
            # Initialize checker
            _checker = test_checker(check_url)

            # Check if can get chapter list
            chapter_list = _checker.get_latest_chapter_list()
            self.validate_chapter_list(chapter_list)
        else:
            self.skipTest(f"{check_url} is not healthy")

    # Novel Checkers
    def test_syosetu_checker(self):
        """Syosetu"""
        self.universal_checking(
            test_checker=checkers.SyosetuChecker,
            check_url="https://ncode.syosetu.com/n6621fl",
        )

    def test_wutuxs_checker(self):
        """Wutuxs"""
        self.universal_checking(
            test_checker=checkers.WutuxsChecker,
            check_url="http://www.wutuxs.com/html/9/9715/",
        )

    def test_wx_checker(self):
        """99wx"""
        self.universal_checking(
            test_checker=checkers.WxChecker,
            check_url="https://www.99wx.cc/wanxiangzhiwang/",
        )

    # Comic Checkers
    def test_manhuagui_checker(self):
        """Manhuagui"""
        self.universal_checking(
            test_checker=checkers.ManhuaguiChecker,
            check_url="https://m.manhuagui.com/comic/30903/",
        )

    def test_qiman_checker(self):
        """Qiman6"""
        self.universal_checking(
            test_checker=checkers.QimanChecker,
            check_url="http://qiman57.com/19827/",
        )

    def test_baozimh_checker(self):
        """Baozimh"""
        self.universal_checking(
            test_checker=checkers.BaozimhChecker,
            check_url=(
                "https://www.baozimh.com/comic/fangkainagenuwu-yuewenmanhua_e"
            ),
        )

    def test_xbiquge_checker(self):
        """Xbiquge"""
        self.universal_checking(
            test_checker=checkers.XbiqugeChecker,
            check_url="https://www.xbiquge.la/55/55945/",
        )

    def test_dashuhuwai_checker(self):
        """Dashuhuwai"""
        self.universal_checking(
            test_checker=checkers.DashuhuwaiChecker,
            check_url="https://www.dashuhuwai.com/comic/fangkainagenvwu/",
        )
