"""Focused tests for the Baozimh (baozimh.com) checker."""

import hashlib
import unittest
from unittest.mock import patch

from bs4 import BeautifulSoup

from helpers.checkers import get_checker_for_url
from helpers.checkers.baozimh import (
    GATEKEEPER_POW_PREFIX,
    BaozimhChecker,
    leading_zero_bits,
)


class TestBaozimhChecker(unittest.TestCase):
    """Validate Baozimh checker wiring, gatekeeper PoW and chapter sorting."""

    def test_get_checker_for_url_returns_baozimh_checker(self) -> None:
        checker = get_checker_for_url(
            "https://www.baozimh.com/comic/sample-title-author"
        )

        self.assertIsInstance(checker, BaozimhChecker)

    def test_leading_zero_bits(self) -> None:
        self.assertEqual(leading_zero_bits(bytes([0b11111111])), 0)
        self.assertEqual(leading_zero_bits(bytes([0b01111111])), 1)
        self.assertEqual(leading_zero_bits(bytes([0x00, 0b00111111])), 10)

    def test_solve_gatekeeper_finds_valid_nonce(self) -> None:
        nonce = BaozimhChecker.solve_gatekeeper("challenge-id", 8)

        digest = hashlib.sha256(
            f"{GATEKEEPER_POW_PREFIX}challenge-id:{nonce}".encode()
        ).digest()
        self.assertGreaterEqual(leading_zero_bits(digest), 8)

    @patch.object(BaozimhChecker, "get_latest_soup")
    def test_get_latest_chapter_list_sorts_chapters_numerically(
        self, mock_get_latest_soup
    ) -> None:
        mock_get_latest_soup.return_value = BeautifulSoup(
            """
            <div class="pure-g">
                <a class="comics-chapters__item" href="/user/page_direct?chapter_slot=47">第47話</a>
                <a class="comics-chapters__item" href="/user/page_direct?chapter_slot=9">第9話</a>
                <a class="comics-chapters__item" href="/user/page_direct?chapter_slot=10">第10話</a>
            </div>
            """,
            "html.parser",
        )

        chapter_list = BaozimhChecker(
            "https://www.baozimh.com/comic/sample-title-author"
        ).get_latest_chapter_list()

        self.assertEqual(
            [chapter.title for chapter in chapter_list],
            ["第9话", "第10话", "第47话"],
        )


if __name__ == "__main__":
    unittest.main()
