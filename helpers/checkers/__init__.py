"""Checkers"""

from typing import List

from helpers.chapter import Chapter
from helpers.checkers.asurascans import AsurascansChecker
from helpers.checkers.baozimh import BaozimhChecker
from helpers.checkers.baozimh2 import Baozimh2Checker
from helpers.checkers.base import AbstractChapterChecker
from helpers.checkers.bilibili_articles import BilibiliArticlesChecker
from helpers.checkers.biqu import BiquChecker
from helpers.checkers.comick import ComickChecker
from helpers.checkers.dashuhuwai import DashumanhuaChecker
from helpers.checkers.jmanga import JmangaChecker
from helpers.checkers.kakuyomu import KakuyomuChecker
from helpers.checkers.laimanhua import LaimanhuaChecker
from helpers.checkers.linovelib import LinovelibChecker
from helpers.checkers.mangaraw import MangarawChecker
from helpers.checkers.manhuagui import ManhuaguiChecker
from helpers.checkers.piaotian import PiaotianChecker
from helpers.checkers.pickmeupgacha import PickmeupgachaChecker
from helpers.checkers.syosetu import SyosetuChecker
from helpers.checkers.weixin import WeixinChecker
from helpers.checkers.wx import WxChecker
from helpers.checkers.xbiquge import XbiqugeChecker

ALL_CHECKERS: List[AbstractChapterChecker] = [
    AsurascansChecker,
    BilibiliArticlesChecker,
    WxChecker,
    SyosetuChecker,
    KakuyomuChecker,
    PiaotianChecker,
    ManhuaguiChecker,
    DashumanhuaChecker,
    BaozimhChecker,
    Baozimh2Checker,
    BiquChecker,
    ComickChecker,
    XbiqugeChecker,
    JmangaChecker,
    WeixinChecker,
    LaimanhuaChecker,
    LinovelibChecker,
    MangarawChecker,
    PickmeupgachaChecker,
]


def get_checker_for_url(url):
    """Return an initialized checker instance based on URL substring match.

    Args:
        url (str): URL of the comic/novel index page

    Returns:
        AbstractChapterChecker | None: Checker instance if matched; otherwise None
    """
    for Checker in ALL_CHECKERS:
        if Checker.URL_SUBSTRING in url:
            return Checker(url)
    return None
