"""Regression: an anime with zero episodes when the checker was added must
have its first episode announced once it appears, instead of being swallowed
as startup backfill."""

import threading
import unittest
from unittest.mock import patch

import requests
import schedule as schedule_lib

from helpers.chapter import Chapter
from helpers.checkers.base import AbstractChapterChecker
from helpers.media import get_checker_for_url as real_get_checker_for_url
from helpers.media_list_state import MediaListState
from helpers.schedule import ScheduleHelper


class StubChecker(AbstractChapterChecker):
    """Checker returning a scripted chapter list."""

    URL_SUBSTRING = "stub.example.com/"

    def __init__(self, check_url: str) -> None:
        super().__init__(check_url)
        self.results = []
        self.fail_next = False
        self.none_next = False

    def get_latest_chapter_list(self):
        if self.fail_next:
            self.fail_next = False
            # routes through the safe wrapper's None path
            raise requests.exceptions.ConnectionError("transient network failure")
        if self.none_next:
            self.none_next = False
            # a checker that signals failure WITHOUT raising, like syosetu
            return None
        return self.results


class FakeTgHelper:
    """Capture sent messages."""

    def __init__(self) -> None:
        self.sent = []

    async def send_msg(self, content: str = "") -> None:
        self.sent.append(content)


class InlineThread(threading.Thread):
    """Run scheduled jobs synchronously."""

    def start(self) -> None:
        self.run()


def stub_get_checker_for_url(url: str) -> AbstractChapterChecker:
    """Match stub URLs to StubChecker, otherwise the real factory."""
    if StubChecker.URL_SUBSTRING in url:
        return StubChecker(url)
    return real_get_checker_for_url(url)


class TestBornEmptyAnime(unittest.TestCase):
    """Add checker while the producer has no episode, then ep1 goes up."""

    def setUp(self) -> None:
        self.tg = FakeTgHelper()
        yml_data = [
            {"name": "TestAnime", "anime_urls": ["https://stub.example.com/1"]}
        ]
        self._checker_patch = patch(
            "helpers.media.get_checker_for_url", stub_get_checker_for_url
        )
        self._thread_patch = patch(
            "helpers.schedule.threading.Thread", InlineThread
        )
        self._checker_patch.start()
        self._thread_patch.start()
        self.addCleanup(self._checker_patch.stop)
        self.addCleanup(self._thread_patch.stop)
        ScheduleHelper(yml_data=yml_data, tg_helper=self.tg)
        self.helper = MediaListState.media_helper_list[0]

    def tearDown(self) -> None:
        MediaListState.media_helper_list = []

    def test_first_episode_announced_after_empty_observation(self) -> None:
        """Episode 1 announced after a confirmed-empty fetch, ep2 not repeated."""
        # Checker added while no episode exists: first fetch is empty
        self.assertEqual(self.helper.checker.chapter_list, [])
        self.assertTrue(self.helper.checker.observed_empty)
        self.assertEqual(self.tg.sent, [])

        # Episode 1 appears: must be announced
        self.helper.checker.results = [Chapter("第1話", "https://v/BV1")]
        schedule_lib.jobs[0].job_func()
        self.assertEqual(len(self.tg.sent), 1)
        self.assertIn("第1話", self.tg.sent[0])

        # ...and episode 2 announced only once, without repeating ep1
        self.helper.checker.results = [
            Chapter("第1話", "https://v/BV1"),
            Chapter("第2話", "https://v/BV2"),
        ]
        schedule_lib.jobs[0].job_func()
        self.assertEqual(len(self.tg.sent), 2)
        self.assertIn("第2話", self.tg.sent[1])
        self.assertNotIn("BV1", self.tg.sent[1])

    def test_restart_backfill_is_still_suppressed(self) -> None:
        """Startup backlog is still baselined silently."""
        # Bot restarts with a backlog: whole list baseline, no announcement
        helper2 = MediaListState.media_helper_list[0]
        helper2.checker.observed_empty = False
        helper2.checker.results = [Chapter("第1話", "https://v/BV1")]
        schedule_lib.jobs[0].job_func()
        self.assertEqual(self.tg.sent, [])
        self.assertEqual(len(helper2.checker.chapter_list), 1)

    def test_fetch_failure_is_not_observed_empty(self) -> None:
        """A failed fetch must not mark observed_empty (it reads as None)."""
        helper = MediaListState.media_helper_list[0]
        helper.checker.observed_empty = False
        helper.checker.fail_next = True
        schedule_lib.jobs[0].job_func()
        self.assertFalse(helper.checker.observed_empty)
        self.assertEqual(self.tg.sent, [])

    def test_none_signalled_failure_is_not_observed_empty(self) -> None:
        """A None-signalled fetch failure must not mark observed_empty."""
        helper = MediaListState.media_helper_list[0]
        helper.checker.observed_empty = False
        helper.checker.none_next = True
        schedule_lib.jobs[0].job_func()
        self.assertFalse(helper.checker.observed_empty)
        self.assertEqual(self.tg.sent, [])

        # The next successful fetch is startup backfill, announced to nobody
        helper.checker.results = [
            Chapter("第1話", "https://v/BV1"),
            Chapter("第2話", "https://v/BV2"),
        ]
        schedule_lib.jobs[0].job_func()
        self.assertEqual(self.tg.sent, [])
        self.assertEqual(len(helper.checker.chapter_list), 2)


if __name__ == "__main__":
    unittest.main()
