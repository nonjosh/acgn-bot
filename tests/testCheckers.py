import unittest
from helpers import Chapter
import helpers.checkers as checkers


class TestCheckers(unittest.TestCase):
    """Check if can get chapter list for each Checker"""

    def validate_chapter_list(self, chapter_list: list):
        """Validate chapter list"""
        # Check if the list item is an Chapter object
        self.assertIsInstance(chapter_list[0], Chapter)

        # Check if the chapter list is not empty
        self.assertGreater(len(chapter_list), 0)

    # Novel Checkers
    def test_syosetu_checker(self):
        """Syosetu"""
        # Initialize checker
        syosetu_checker = checkers.SyosetuChecker(
            check_url="https://ncode.syosetu.com/n6621fl"
        )

        # Check if can get chapter list
        chapter_list = syosetu_checker.get_latest_chapter_list()
        self.validate_chapter_list(chapter_list)

    def test_wutuxs_checker(self):
        """Wutuxs"""
        # Initialize checker
        wutuxs_checker = checkers.WutuxsChecker(
            check_url="http://www.wutuxs.com/html/9/9715/"
        )

        # Check if can get chapter list
        chapter_list = wutuxs_checker.get_latest_chapter_list()
        self.validate_chapter_list(chapter_list)

    # Comic Checkers
    def test_manhuagui_checker(self):
        """Manhuagui"""
        # Initialize checker
        check_url = "https://m.manhuagui.com/comic/30903/"
        manhuagui_checker = checkers.ManhuaguiChecker(check_url)

        # Check if can get chapter list
        chapter_list = manhuagui_checker.get_latest_chapter_list()
        self.validate_chapter_list(chapter_list)

    def test_qiman_checker(self):
        """Qiman6"""
        # Initialize checker
        check_url = "http://qiman57.com/19827/"
        qiman6_checker = checkers.QimanChecker(check_url)

        # Check if can get chapter list
        chapter_list = qiman6_checker.get_latest_chapter_list()
        self.validate_chapter_list(chapter_list)

    def test_baozimh_checker(self):
        """Baozimh"""
        # Initialize checker
        check_url = (
            "https://www.baozimh.com/comic/fangkainagenuwu-yuewenmanhua_e"
        )
        baozimh_checker = checkers.BaozimhChecker(check_url)

        # Check if can get chapter list
        chapter_list = baozimh_checker.get_latest_chapter_list()
        self.validate_chapter_list(chapter_list)

    def test_xbiquge_checker(self):
        """Xbiquge"""
        # Initialize checker
        check_url = "https://www.xbiquge.la/55/55945/"
        xbiquge_checker = checkers.XbiqugeChecker(check_url)

        # Check if can get chapter list
        chapter_list = xbiquge_checker.get_latest_chapter_list()
        self.validate_chapter_list(chapter_list)
