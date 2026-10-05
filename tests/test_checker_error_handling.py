"""Regression tests for checker and schedule error handling."""

import unittest
from unittest.mock import Mock, patch

import requests

from helpers.chapter import Chapter
from helpers.checkers.base import AbstractChapterChecker
from helpers.checkers.syosetu import SyosetuChecker
from helpers.schedule import ScheduleHelper


class NoopChecker(AbstractChapterChecker):
    """Minimal checker for testing base request helpers."""

    def get_latest_chapter_list(self):
        return []


class TestCheckerErrorHandling(unittest.TestCase):
    """Fetch helpers retry transient failures then surface them to callers."""

    @patch("backoff._sync.time.sleep", return_value=None)
    @patch(
        "helpers.checkers.base.requests.get",
        side_effect=requests.exceptions.ReadTimeout("timed out"),
    )
    def test_get_latest_response_retries_then_raises_on_timeout(
        self, mock_get, _mock_sleep
    ) -> None:
        """Transient failures are retried (backoff) before failing loudly."""
        checker = NoopChecker("https://example.com")

        with self.assertRaises(requests.exceptions.ReadTimeout):
            checker.get_latest_response()

        # max_tries=3 configured on get_latest_response
        self.assertEqual(mock_get.call_count, 3)

    @patch("backoff._sync.time.sleep", return_value=None)
    @patch(
        "helpers.checkers.base.requests.post",
        side_effect=requests.exceptions.ReadTimeout("timed out"),
    )
    def test_get_latest_post_response_retries_then_raises_on_timeout(
        self, mock_post, _mock_sleep
    ) -> None:
        checker = NoopChecker("https://example.com")

        with self.assertRaises(requests.exceptions.ReadTimeout):
            checker.get_latest_post_response(data={"id": 1})

        self.assertEqual(mock_post.call_count, 3)

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


class TestSyosetuPartialFetchRegression(unittest.TestCase):
    """GKE sidecar outage regression: a failed last-page fetch must never
    fall back to the page-1 soup, or every known chapter re-appears as new."""

    CHECK_URL = "https://ncode.syosetu.com/n4449cj"

    PAGE1_HTML = """
    <html><body>
      <a class="c-pager__item--last" href="/n4449cj/?p=2">last</a>
      <a class="p-eplist__subtitle" href="/n4449cj/1/">Its first chapter</a>
      <a class="p-eplist__subtitle" href="/n4449cj/2/">Its second chapter</a>
    </body></html>
    """

    PAGE2_HTML = """
    <html><body>
      <a class="p-eplist__subtitle" href="/n4449cj/3/">Its third chapter</a>
      <a class="p-eplist__subtitle" href="/n4449cj/4/">Its fourth chapter</a>
    </body></html>
    """

    @staticmethod
    def make_response(text: str) -> requests.models.Response:
        response = requests.models.Response()
        response.status_code = 200
        # pylint: disable-next=protected-access
        response._content = text.encode("utf-8")
        response.encoding = "utf-8"
        response.headers = {}
        return response

    @patch("backoff._sync.time.sleep", return_value=None)
    @patch("helpers.checkers.base.requests.get")
    def test_last_page_failure_returns_empty_list(self, mock_get, _mock_sleep) -> None:
        def fake_get(**_kwargs):
            if mock_get.call_count == 1:
                return self.make_response(self.PAGE1_HTML)
            raise requests.exceptions.ConnectionError("proxy down")

        mock_get.side_effect = fake_get
        checker = SyosetuChecker(self.CHECK_URL)

        # Empty list means "fetch failed" to base: no diff, no notification.
        self.assertEqual(checker.get_latest_chapter_list(), [])

        # The last page was requested exactly once (after backoff retries).
        self.assertEqual(mock_get.call_count, 4)
        self.assertEqual(
            mock_get.call_args_list[1].kwargs["url"],
            "https://ncode.syosetu.com/n4449cj/?p=2",
        )

    @patch("backoff._sync.time.sleep", return_value=None)
    @patch("helpers.checkers.base.requests.get")
    def test_last_page_success_parses_last_page(self, mock_get, _mock_sleep) -> None:
        mock_get.side_effect = [
            self.make_response(self.PAGE1_HTML),
            self.make_response(self.PAGE2_HTML),
        ]
        checker = SyosetuChecker(self.CHECK_URL)

        chapter_list = checker.get_latest_chapter_list()
        self.assertEqual(
            [(c.title, c.url) for c in chapter_list],
            [
                ("Its third chapter", "https://ncode.syosetu.com/n4449cj/3/"),
                ("Its fourth chapter", "https://ncode.syosetu.com/n4449cj/4/"),
            ],
        )

    @patch("backoff._sync.time.sleep", return_value=None)
    @patch("helpers.checkers.base.requests.get")
    def test_partial_fetch_does_not_poison_state_nor_diff(
        self, mock_get, _mock_sleep
    ) -> None:
        checker = SyosetuChecker(self.CHECK_URL)
        old_list = [
            Chapter("Its third chapter", "https://ncode.syosetu.com/n4449cj/3/"),
            Chapter("Its fourth chapter", "https://ncode.syosetu.com/n4449cj/4/"),
        ]
        checker.chapter_list = old_list

        # Simulate base page success + last-page failure (the outage pattern).
        def fake_get(**_kwargs):
            if mock_get.call_count == 1:
                return self.make_response(self.PAGE1_HTML)
            raise requests.exceptions.ConnectionError("proxy down")

        mock_get.side_effect = fake_get

        updated = checker.get_updated_chapter_list()

        # No phantom updates and the known-good list is kept for the next cycle.
        self.assertEqual(updated, [])
        self.assertEqual(checker.chapter_list, old_list)


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
