"""Regression tests for checker network error handling."""

import unittest
from unittest.mock import patch

import requests

from helpers.checkers.base import AbstractChapterChecker


class NoopChecker(AbstractChapterChecker):
    """Minimal checker for testing base request helpers."""

    def get_latest_chapter_list(self):
        return []


class TestCheckerErrorHandling(unittest.TestCase):
    """Ensure transient request failures do not escape checker helpers."""

    @patch("backoff._sync.time.sleep", return_value=None)
    @patch(
        "helpers.checkers.base.requests.get",
        side_effect=requests.exceptions.ReadTimeout("timed out"),
    )
    def test_get_latest_response_returns_none_on_timeout(
        self, _mock_get, _mock_sleep
    ) -> None:
        checker = NoopChecker("https://example.com")

        try:
            response = checker.get_latest_response()
        except requests.exceptions.ReadTimeout as err:
            self.fail(f"get_latest_response should not raise ReadTimeout: {err}")

        self.assertIsNone(response)

    @patch("backoff._sync.time.sleep", return_value=None)
    @patch(
        "helpers.checkers.base.requests.post",
        side_effect=requests.exceptions.ReadTimeout("timed out"),
    )
    def test_get_latest_post_response_returns_empty_list_on_timeout(
        self, _mock_post, _mock_sleep
    ) -> None:
        checker = NoopChecker("https://example.com")

        try:
            response = checker.get_latest_post_response(data={"id": 1})
        except requests.exceptions.ReadTimeout as err:
            self.fail(f"get_latest_post_response should not raise ReadTimeout: {err}")

        self.assertEqual(response, [])
