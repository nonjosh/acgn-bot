"""Regression tests for checker and schedule error handling."""

import unittest
from unittest.mock import Mock, patch

import requests

from helpers.checkers.base import AbstractChapterChecker
from helpers.schedule import ScheduleHelper


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

    class RaiseChecker(AbstractChapterChecker):
        """Checker that always raises in list retrieval."""

        def get_latest_chapter_list(self):
            raise requests.exceptions.RequestException("Unexpected status code: 404")

    def test_get_updated_chapter_list_returns_empty_on_checker_exception(self) -> None:
        checker = self.RaiseChecker("https://example.com")

        try:
            response = checker.get_updated_chapter_list()
        except requests.exceptions.RequestException as err:
            self.fail(
                "get_updated_chapter_list should not raise RequestException: "
                f"{err}"
            )

        self.assertEqual(response, [])


class TestScheduleErrorHandling(unittest.TestCase):
    """Ensure schedule job boundary catches checker failures."""

    @patch("helpers.schedule.schedule.every")
    @patch("helpers.schedule.threading.Thread")
    def test_add_schedule_does_not_crash_on_checker_exception(
        self, mock_thread: Mock, mock_every: Mock
    ) -> None:
        schedule_helper = ScheduleHelper.__new__(ScheduleHelper)
        schedule_helper.tg_helper = Mock()

        media_helper = Mock()
        media_helper.media_type = "comic"
        media_helper.name = "Broken checker"
        media_helper.urls = ["https://example.com/broken"]
        media_helper.check_url = "https://example.com/broken"
        media_helper.checker = Mock()
        media_helper.checker.chapter_list = []
        media_helper.checker.get_updated_chapter_list.side_effect = (
            requests.exceptions.RequestException("Unexpected status code: 404")
        )

        mock_job = Mock()
        mock_job.minutes = Mock()
        mock_job.minutes.do = Mock()
        mock_every.return_value.to.return_value = mock_job

        captured_target = {}

        def fake_thread(*, target):
            captured_target["target"] = target
            fake = Mock()
            fake.start = Mock()
            return fake

        mock_thread.side_effect = fake_thread

        schedule_helper.add_schedule(media_helper)

        # Simulate first immediate run in thread.
        self.assertIn("target", captured_target)
        captured_target["target"]()
