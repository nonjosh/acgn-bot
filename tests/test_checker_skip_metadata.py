"""Regression tests for checker skip metadata."""

import os
import unittest
from unittest.mock import patch

import tests.test_checkers as checker_tests


class TestCheckerSkipMetadata(unittest.TestCase):
    """Ensure GitHub-only skips stay scoped to CI."""

    def test_github_actions_skip_only_applies_in_github_actions(self) -> None:
        with patch.dict(os.environ, {}, clear=True):
            decorated = checker_tests.github_actions_skip("GitHub-only skip")(lambda: None)
            self.assertFalse(getattr(decorated, "__unittest_skip__", False))
            self.assertEqual(getattr(decorated, "__unittest_skip_why__", ""), "")

        with patch.dict(os.environ, {"GITHUB_ACTIONS": "true"}, clear=True):
            decorated = checker_tests.github_actions_skip("GitHub-only skip")(lambda: None)
            self.assertTrue(getattr(decorated, "__unittest_skip__", False))
            self.assertEqual(
                getattr(decorated, "__unittest_skip_why__", ""),
                "GitHub-only skip",
            )

    def test_github_only_sites_are_not_skipped_locally_by_default(self) -> None:
        locally_enabled = (
            "test_asurascans_integration",
            "test_dashumanhua_checker",
            "test_jmanga_checker",
            "test_pickmeupgacha_checker",
            "test_weixin_checker",
            "test_xbiquge_checker",
        )

        for test_name in locally_enabled:
            with self.subTest(test_name=test_name):
                test_method = getattr(checker_tests.TestCheckers, test_name)
                self.assertFalse(getattr(test_method, "__unittest_skip__", False))


if __name__ == "__main__":
    unittest.main()
