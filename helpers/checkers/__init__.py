"""Checkers"""
from typing import List
from helpers.chapter import Chapter
from helpers.checkers.base import AbstractChapterChecker
from helpers.checkers.wx import WxChecker
from helpers.checkers.syosetu import SyosetuChecker
from helpers.checkers.piaotian import PiaotianChecker
from helpers.checkers.six_nine_shu_ba import SixNineShuBaChecker
from helpers.checkers.manhuagui import ManhuaguiChecker
from helpers.checkers.qiman import QimanChecker
from helpers.checkers.baozimh import BaozimhChecker
from helpers.checkers.baozimh2 import Baozimh2Checker
from helpers.checkers.dashuhuwai import DashumanhuaChecker
from helpers.checkers.mn4u import Mn4uChecker
from helpers.checkers.xbiquge import XbiqugeChecker
from helpers.checkers.klmanaga import KlmanagaChecker
from helpers.checkers.kunmanga import KunmangaChecker
from helpers.checkers.weixin import WeixinChecker

ALL_CHECKERS: List[AbstractChapterChecker] = [
    WxChecker,
    SyosetuChecker,
    PiaotianChecker,
    SixNineShuBaChecker,
    ManhuaguiChecker,
    QimanChecker,
    BaozimhChecker,
    Baozimh2Checker,
    DashumanhuaChecker,
    Mn4uChecker,
    XbiqugeChecker,
    KlmanagaChecker,
    KunmangaChecker,
    WeixinChecker,
]


def get_checker_for_url(url):
    for Checker in ALL_CHECKERS:
        if Checker.URL_SUBSTRING in url:
            return Checker(url)
