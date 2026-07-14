"""Focused tests for anime media type support."""

import unittest
from unittest.mock import Mock, patch

from helpers.media import MediaHelper
from helpers.media_list_state import MediaListState
from helpers.message import MessageHelper
from helpers.schedule import ScheduleHelper
from helpers.yml_parser import YmlParser


class TestAnimeMediaSupport(unittest.TestCase):
    """Validate anime media type wiring across helper layers."""

    def setUp(self) -> None:
        self._original_media_helper_list = MediaListState.media_helper_list
        MediaListState.media_helper_list = []

    def tearDown(self) -> None:
        MediaListState.media_helper_list = self._original_media_helper_list

    @patch("helpers.media.get_checker_for_url")
    @patch("helpers.media.check_url_valid", return_value=True)
    def test_media_helper_accepts_anime_type(
        self, _mock_check_url_valid: Mock, mock_get_checker_for_url: Mock
    ) -> None:
        mock_checker = Mock()
        mock_get_checker_for_url.return_value = mock_checker

        helper = MediaHelper(
            name="Test Anime",
            urls=["https://space.bilibili.com/690151424/lists/8495686?type=season"],
            media_type="anime",
        )

        self.assertEqual(helper.media_type, "anime")
        self.assertIs(helper.checker, mock_checker)

    def test_yml_parser_accepts_anime_urls(self) -> None:
        parser = YmlParser.__new__(YmlParser)
        parser.yml_data = [
            {
                "name": "Test Anime",
                "anime_urls": [
                    "https://space.bilibili.com/690151424/lists/8495686?type=season"
                ],
            }
        ]

        self.assertTrue(parser.validate())

    def test_yml_parser_rejects_non_list_anime_urls(self) -> None:
        parser = YmlParser.__new__(YmlParser)
        parser.yml_data = [
            {
                "name": "Test Anime",
                "anime_urls": "https://space.bilibili.com/690151424/lists/8495686?type=season",
            }
        ]

        self.assertFalse(parser.validate())

    def test_message_helper_renders_anime_group(self) -> None:
        anime_helper = Mock()
        anime_helper.media_type = "anime"
        anime_helper.name = "Test Anime"
        anime_helper.get_urls_text.return_value = (
            "<a href='https://space.bilibili.com'>bilibili</a>\n"
        )
        anime_helper.checker = None
        MediaListState.media_helper_list = [anime_helper]

        html_response = MessageHelper().get_config_list_html_message()

        self.assertIn("<b>Anime</b>", html_response)
        self.assertIn("Test Anime", html_response)

    @patch("helpers.schedule.schedule.clear")
    @patch("helpers.schedule.ScheduleHelper.add_schedule")
    @patch("helpers.schedule.MediaHelper")
    def test_schedule_helper_creates_anime_helper_from_anime_urls(
        self,
        mock_media_helper: Mock,
        mock_add_schedule: Mock,
        _mock_schedule_clear: Mock,
    ) -> None:
        helper_instance = Mock()
        mock_media_helper.return_value = helper_instance
        MediaListState.media_helper_list = []

        with patch("helpers.schedule.schedule.jobs", [object()]):
            ScheduleHelper(
                yml_data=[
                    {
                        "name": "Test Anime",
                        "anime_urls": [
                            "https://space.bilibili.com/690151424/lists/8495686?type=season"
                        ],
                    }
                ],
                tg_helper=Mock(),
            )

        mock_media_helper.assert_called_once_with(
            name="Test Anime",
            urls=["https://space.bilibili.com/690151424/lists/8495686?type=season"],
            media_type="anime",
        )
        self.assertEqual(MediaListState.media_helper_list, [helper_instance])
        mock_add_schedule.assert_called_once_with(helper_instance)


if __name__ == "__main__":
    unittest.main()
