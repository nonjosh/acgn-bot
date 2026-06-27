"""Focused tests for the Mangaraw checker."""

import unittest
from unittest.mock import Mock, patch

from helpers.chapter import Chapter
from helpers.checkers.mangaraw import MangarawChecker


class TestMangarawChecker(unittest.TestCase):
    """Validate Mangaraw URL parsing and chapter mapping."""

    def test_extract_manga_id(self) -> None:
        self.assertEqual(
            MangarawChecker._extract_manga_id("https://mangaraw.co.uk/manga/2439"),
            "2439",
        )
        self.assertEqual(
            MangarawChecker._extract_manga_id("https://mangaraw.co.uk/manga/2439/"),
            "2439",
        )
        self.assertIsNone(
            MangarawChecker._extract_manga_id("https://mangaraw.co.uk/chapter/419376")
        )

    @patch.object(MangarawChecker, "get_latest_response")
    def test_get_latest_chapter_list_uses_api_payload(
        self, mock_get_latest_response: Mock
    ) -> None:
        mock_response = Mock()
        mock_response.json.return_value = {
            "data": [
                {"id": 419376, "title": "Chapter 69", "index": 69},
                {"id": 117692, "title": "Chapter 1", "index": 1},
                {"id": 200000, "title": "", "index": 70},
                {"id": None, "title": "skip me", "index": 71},
            ]
        }
        mock_get_latest_response.return_value = mock_response

        checker = MangarawChecker("https://mangaraw.co.uk/manga/2439")

        self.assertEqual(
            checker.get_latest_chapter_list(),
            [
                Chapter(
                    title="Chapter 1",
                    url="https://mangaraw.co.uk/chapter/117692",
                ),
                Chapter(
                    title="Chapter 69",
                    url="https://mangaraw.co.uk/chapter/419376",
                ),
                Chapter(
                    title="https://mangaraw.co.uk/chapter/200000",
                    url="https://mangaraw.co.uk/chapter/200000",
                ),
            ],
        )
        mock_get_latest_response.assert_called_once_with(
            url="https://api.mangarw.com/api/v1/manga/2439/chapters",
            apparent_encoding=False,
        )

    @patch.object(MangarawChecker, "get_latest_response")
    def test_invalid_url_skips_api_call(self, mock_get_latest_response: Mock) -> None:
        checker = MangarawChecker("https://mangaraw.co.uk/chapter/419376")

        self.assertEqual(checker.get_latest_chapter_list(), [])
        mock_get_latest_response.assert_not_called()


if __name__ == "__main__":
    unittest.main()
