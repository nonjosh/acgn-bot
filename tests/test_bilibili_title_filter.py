"""Focused tests for the Bilibili promo-title filter."""

import unittest
from unittest.mock import Mock, patch

from helpers.checkers.bilibili_channel_series import BilibiliChannelSeriesChecker
from helpers.checkers.bilibili_common import is_noise_title
from helpers.checkers.bilibili_uploader import BilibiliUploaderChecker


class TestBilibiliNoiseTitleFilter(unittest.TestCase):
    """Promo/preview titles must not reach the chapter list (and Telegram)."""

    def test_is_noise_title_matches_simplified_and_traditional(self) -> None:
        for title in (
            "PV",
            "【PV】第2弾",
            "第1話PV",
            "第1話 迷你動畫",
            "先行圖公開",
            "先行图",
            "先行図",
        ):
            self.assertTrue(is_noise_title(title), title)

        for title in (
            "轉生重騎士 第1話",
            "藥屋少女的呢喃 第24話",
            "PVP対戦 第1話",
            "",
        ):
            self.assertFalse(is_noise_title(title), title)

    @patch.object(BilibiliUploaderChecker, "_sync_bilibili_cookies")
    @patch.object(BilibiliUploaderChecker, "_search_page")
    def test_uploader_drops_noise_titles(
        self, mock_search_page: Mock, _mock_cookies: Mock
    ) -> None:
        mock_search_page.return_value = [
            {
                "mid": 1,
                "bvid": "BV1PV",
                "title": "亂世千金 PV",
                "hit_columns": ["title"],
                "pubdate": 2,
            },
            {
                "mid": 1,
                "bvid": "BV1EP",
                "title": "亂世千金 第1話",
                "hit_columns": ["title"],
                "pubdate": 1,
            },
        ]

        checker = BilibiliUploaderChecker(
            "https://space.bilibili.com/1/upload/video?keyword=亂世千金"
        )

        self.assertEqual(
            [chapter.url for chapter in checker.get_latest_chapter_list()],
            ["https://www.bilibili.com/video/BV1EP"],
        )

    @patch.object(BilibiliChannelSeriesChecker, "get_latest_response")
    def test_channel_series_drops_noise_titles(
        self, mock_get_latest_response: Mock
    ) -> None:
        mock_response = Mock()
        mock_response.json.return_value = {
            "code": 0,
            "data": {
                "archives": [
                    {"bvid": "BV1PV", "title": "先行圖", "pubdate": 2},
                    {"bvid": "BV1EP", "title": "Episode 1", "pubdate": 1},
                ],
                "page": {"total": 2},
            },
        }
        mock_get_latest_response.return_value = mock_response

        checker = BilibiliChannelSeriesChecker(
            "https://space.bilibili.com/690151424/lists/8495686?type=season"
        )

        self.assertEqual(
            [chapter.url for chapter in checker.get_latest_chapter_list()],
            ["https://www.bilibili.com/video/BV1EP"],
        )


if __name__ == "__main__":
    unittest.main()
