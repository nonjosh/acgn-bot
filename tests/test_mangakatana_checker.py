"""Focused tests for the Mangakatana checker."""

import unittest
from unittest.mock import Mock, patch

from bs4 import BeautifulSoup

from helpers.chapter import Chapter
from helpers.checkers import get_checker_for_url
from helpers.checkers.mangakatana import MangakatanaChecker


class TestMangakatanaChecker(unittest.TestCase):
    """Validate Mangakatana checker wiring and parsing."""

    def test_get_checker_for_url_returns_checker(self) -> None:
        checker = get_checker_for_url(
            "https://mangakatana.com/manga/brutal-daughter-nia-liston-a-splendid-matchless-record-of-a-god-slaying-warrior-reincarnated-as-a-sickly-daughter.27292"
        )

        self.assertIsNotNone(checker)
        if checker is None:
            self.fail("Expected a Mangakatana checker instance")

        self.assertIsInstance(checker, MangakatanaChecker)

    @patch.object(MangakatanaChecker, "get_latest_soup")
    def test_get_latest_chapter_list_parses_chapter_table(
        self, mock_get_latest_soup: Mock
    ) -> None:
        mock_get_latest_soup.return_value = BeautifulSoup(
            """
            <div class="chapters">
                <table>
                    <tbody>
                        <tr>
                            <td><div class="chapter"><a href="https://mangakatana.com/manga/sample-title.123/c3">Chapter 3</a></div></td>
                        </tr>
                        <tr>
                            <td><div class="chapter"><a href="https://mangakatana.com/manga/sample-title.123/c2">Chapter 2</a></div></td>
                        </tr>
                        <tr>
                            <td><div class="chapter"><a href="https://mangakatana.com/manga/sample-title.123/c1">Chapter 1</a></div></td>
                        </tr>
                        <tr>
                            <td><div class="chapter"><a href="https://example.com/ignore-me">Ignore me</a></div></td>
                        </tr>
                    </tbody>
                </table>
            </div>
            """,
            "html.parser",
        )

        checker = MangakatanaChecker(
            "https://mangakatana.com/manga/sample-title.123"
        )

        self.assertEqual(
            checker.get_latest_chapter_list(),
            [
                Chapter(
                    title="Chapter 1",
                    url="https://mangakatana.com/manga/sample-title.123/c1",
                ),
                Chapter(
                    title="Chapter 2",
                    url="https://mangakatana.com/manga/sample-title.123/c2",
                ),
                Chapter(
                    title="Chapter 3",
                    url="https://mangakatana.com/manga/sample-title.123/c3",
                ),
            ],
        )


if __name__ == "__main__":
    _ = unittest.main()
