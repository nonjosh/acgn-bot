"""Focused tests for the Bilibili uploader keyword checker."""

import unittest
from unittest.mock import Mock, patch

import requests

from helpers.checkers.bilibili_uploader import BilibiliUploaderChecker

CHECK_URL = "https://space.bilibili.com/690151424/upload/video?keyword=psyren"


def home_response() -> Mock:
    response = Mock()
    response.headers = {
        "set-cookie": (
            "buvid3=HOME3; path=/; expires=Wed, 01 Jan 2026 00:00:00 GMT, "
            "b_nut=1700000000; path=/"
        )
    }
    return response


def spi_response(b_3: str = "SPI3", b_4: str = "SPI4") -> Mock:
    response = Mock()
    response.json.return_value = {"code": 0, "data": {"b_3": b_3, "b_4": b_4}}
    return response


def search_response() -> Mock:
    response = Mock()
    response.json.return_value = {
        "code": 0,
        "data": {
            "result": [
                {
                    "mid": 690151424,
                    "bvid": "BV1TEST00001",
                    "title": "ep1",
                    "pubdate": 2,
                    "hit_columns": ["title"],
                },
                {
                    "mid": 111111,
                    "bvid": "BVOTHER",
                    "title": "other",
                    "pubdate": 3,
                },
            ]
        },
    }
    return response


def filler_search_response() -> Mock:
    """Keyword search tail: same uploader, but the keyword matched nothing."""
    response = Mock()
    response.json.return_value = {
        "code": 0,
        "data": {
            "result": [
                {
                    "mid": 690151424,
                    "bvid": "BV1FILLER01",
                    "title": "4K简中【颠公与圣母 开局就撕衣爆头】全12话（未删减）",
                    "pubdate": 5,
                    "hit_columns": [],
                }
            ]
        },
    }
    return response


class TestBilibiliUploaderChecker(unittest.TestCase):
    """Validate cookie seeding (buvid3/buvid4 via finger/spi) and 412 handling."""

    def setUp(self) -> None:
        BilibiliUploaderChecker._cookie_cache = {}

    @patch.object(BilibiliUploaderChecker, "get_latest_response")
    def test_cookie_jar_from_home_and_spi(self, mock_get: Mock) -> None:
        mock_get.side_effect = [home_response(), spi_response(), search_response()]

        checker = BilibiliUploaderChecker(CHECK_URL)
        chapters = checker.get_latest_chapter_list()

        cookie = checker.headers["Cookie"]
        # spi values overlay home values; b_nut kept from home
        self.assertIn("buvid3=SPI3", cookie)
        self.assertIn("buvid4=SPI4", cookie)
        self.assertIn("b_nut=1700000000", cookie)
        # only the uploader's own videos become chapters
        self.assertEqual([c.url for c in chapters], ["https://www.bilibili.com/video/BV1TEST00001"])
        # home + spi + one search page (2 results < PAGE_SIZE stops the loop before page 2)
        self.assertEqual(mock_get.call_count, 3)

    @patch.object(BilibiliUploaderChecker, "get_latest_response")
    def test_cookie_cache_reused_across_runs(self, mock_get: Mock) -> None:
        mock_get.side_effect = [home_response(), spi_response(), search_response(), search_response()]

        checker = BilibiliUploaderChecker(CHECK_URL)
        checker.get_latest_chapter_list()
        checker.get_latest_chapter_list()

        # second run reuses cached device: no extra home/spi calls
        self.assertEqual(mock_get.call_count, 4)
        self.assertEqual(checker.headers["Cookie"], BilibiliUploaderChecker._cookie_cache["cookie"])

    @patch.object(BilibiliUploaderChecker, "get_latest_response")
    def test_search_412_returns_empty_list(self, mock_get: Mock) -> None:
        mock_get.side_effect = [
            home_response(),
            spi_response(),
            requests.exceptions.RequestException("Unexpected status code: 412"),
        ]

        checker = BilibiliUploaderChecker(CHECK_URL)
        self.assertEqual(checker.get_latest_chapter_list(), [])

    @patch.object(BilibiliUploaderChecker, "get_latest_response")
    def test_cookie_sync_412_returns_empty_list(self, mock_get: Mock) -> None:
        # flagged IP: the home/spi cookie fetch itself 412s
        mock_get.side_effect = requests.exceptions.RequestException(
            "Unexpected status code: 412"
        )

        checker = BilibiliUploaderChecker(CHECK_URL)
        self.assertEqual(checker.get_latest_chapter_list(), [])

    @patch.object(BilibiliUploaderChecker, "get_latest_response")
    def test_keyword_filler_results_dropped(self, mock_get: Mock) -> None:
        # keyword matched no field (hit_columns empty) = bilibili fuzzy filler;
        # must not become a chapter even though the uploader matches
        mock_get.side_effect = [
            home_response(),
            spi_response(),
            filler_search_response(),
        ]

        checker = BilibiliUploaderChecker(CHECK_URL)
        self.assertEqual(checker.get_latest_chapter_list(), [])

    @patch.object(BilibiliUploaderChecker, "get_latest_response")
    def test_ranking_drift_does_not_reannounce(self, mock_get: Mock) -> None:
        # run 1 sees ep1; run 2's search drifts it out and back in via filler
        mock_get.side_effect = [
            home_response(),
            spi_response(),
            search_response(),
            home_response(),
            spi_response(),
            filler_search_response(),
            search_response(),
        ]

        checker = BilibiliUploaderChecker(CHECK_URL)
        first = checker.get_latest_chapter_list()
        self.assertEqual(
            [c.url for c in first], ["https://www.bilibili.com/video/BV1TEST00001"]
        )

        # ep1 dropped out (filler only): list must still keep it, so the base
        # diff cannot treat it as new again
        no_hit_run = checker.get_latest_chapter_list()
        self.assertEqual(
            [c.url for c in no_hit_run], ["https://www.bilibili.com/video/BV1TEST00001"]
        )

        drift_back_run = checker.get_latest_chapter_list()
        self.assertEqual(
            [c.url for c in drift_back_run],
            ["https://www.bilibili.com/video/BV1TEST00001"],
        )


if __name__ == "__main__":
    unittest.main()
