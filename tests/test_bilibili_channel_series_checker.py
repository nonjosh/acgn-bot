"""Focused tests for the Bilibili channel list checker."""

import unittest
from unittest.mock import Mock, call, patch

from helpers.chapter import Chapter
from helpers.checkers import get_checker_for_url
from helpers.checkers.bilibili_channel_series import BilibiliChannelSeriesChecker


class TestBilibiliChannelSeriesChecker(unittest.TestCase):
    """Validate Bilibili channel list URL parsing and API mapping."""

    def test_get_checker_for_url_returns_checker(self) -> None:
        checker = get_checker_for_url(
            "https://space.bilibili.com/690151424/lists/8495686?type=season"
        )

        self.assertIsNotNone(checker)
        if checker is None:
            self.fail("Expected a Bilibili channel list checker instance")

        self.assertIsInstance(checker, BilibiliChannelSeriesChecker)

    def test_extract_channel_info(self) -> None:
        self.assertEqual(
            BilibiliChannelSeriesChecker._extract_channel_info(
                "https://space.bilibili.com/690151424/lists/8495686?type=season"
            ),
            ("690151424", "8495686", "season"),
        )
        self.assertEqual(
            BilibiliChannelSeriesChecker._extract_channel_info(
                "https://space.bilibili.com/690151424/lists/123456?type=series"
            ),
            ("690151424", "123456", "series"),
        )
        self.assertEqual(
            BilibiliChannelSeriesChecker._extract_channel_info(
                "https://space.bilibili.com/690151424/lists/123456"
            ),
            ("690151424", "123456", None),
        )
        self.assertIsNone(
            BilibiliChannelSeriesChecker._extract_channel_info(
                "https://space.bilibili.com/690151424/video"
            )
        )
        self.assertIsNone(
            BilibiliChannelSeriesChecker._extract_channel_info(
                "https://www.bilibili.com/video/BV1ESTX6NEL4"
            )
        )

    @patch.object(BilibiliChannelSeriesChecker, "get_latest_response")
    def test_get_latest_chapter_list_uses_season_api_payload(
        self, mock_get_latest_response: Mock
    ) -> None:
        mock_response = Mock()
        mock_response.json.return_value = {
            "code": 0,
            "data": {
                "archives": [
                    {"bvid": "BV1TEST00002", "title": "Episode 2", "pubdate": 20},
                    {"bvid": "BV1TEST00001", "title": "Episode 1", "pubdate": 10},
                    {"aid": 123456789, "title": "", "pubdate": 30},
                ],
                "page": {"total": 3},
            },
        }
        mock_get_latest_response.return_value = mock_response

        checker = BilibiliChannelSeriesChecker(
            "https://space.bilibili.com/690151424/lists/8495686?type=season"
        )

        self.assertEqual(
            checker.get_latest_chapter_list(),
            [
                Chapter(
                    title="Episode 1",
                    url="https://www.bilibili.com/video/BV1TEST00001",
                ),
                Chapter(
                    title="Episode 2",
                    url="https://www.bilibili.com/video/BV1TEST00002",
                ),
                Chapter(
                    title="https://www.bilibili.com/video/av123456789",
                    url="https://www.bilibili.com/video/av123456789",
                ),
            ],
        )
        mock_get_latest_response.assert_called_once_with(
            url=(
                "https://api.bilibili.com/x/polymer/web-space/"
                "seasons_archives_list?mid=690151424&season_id=8495686"
                "&sort_reverse=true&page_num=1&page_size=100"
            ),
            apparent_encoding=False,
        )

    @patch.object(BilibiliChannelSeriesChecker, "get_latest_response")
    def test_missing_type_falls_back_to_series_api(
        self, mock_get_latest_response: Mock
    ) -> None:
        empty_season_response = Mock()
        empty_season_response.json.return_value = {
            "code": 0,
            "data": {"archives": [], "page": {"total": 0}},
        }
        series_response = Mock()
        series_response.json.return_value = {
            "code": 0,
            "data": {
                "archives": [
                    {"bvid": "BV1SERIES001", "title": "Series Episode 1", "ctime": 10}
                ],
                "page": {"total": 1},
            },
        }
        mock_get_latest_response.side_effect = [
            empty_season_response,
            series_response,
        ]

        checker = BilibiliChannelSeriesChecker(
            "https://space.bilibili.com/690151424/lists/123456"
        )

        self.assertEqual(
            checker.get_latest_chapter_list(),
            [
                Chapter(
                    title="Series Episode 1",
                    url="https://www.bilibili.com/video/BV1SERIES001",
                )
            ],
        )
        self.assertEqual(
            mock_get_latest_response.call_args_list,
            [
                call(
                    url=(
                        "https://api.bilibili.com/x/polymer/web-space/"
                        "seasons_archives_list?mid=690151424&season_id=123456"
                        "&sort_reverse=true&page_num=1&page_size=100"
                    ),
                    apparent_encoding=False,
                ),
                call(
                    url=(
                        "https://api.bilibili.com/x/series/archives"
                        "?mid=690151424&series_id=123456&pn=1&ps=100"
                    ),
                    apparent_encoding=False,
                ),
            ],
        )

    @patch.object(BilibiliChannelSeriesChecker, "get_latest_response")
    def test_invalid_url_skips_api_call(self, mock_get_latest_response: Mock) -> None:
        checker = BilibiliChannelSeriesChecker(
            "https://space.bilibili.com/690151424/video"
        )

        self.assertEqual(checker.get_latest_chapter_list(), [])
        mock_get_latest_response.assert_not_called()


if __name__ == "__main__":
    unittest.main()