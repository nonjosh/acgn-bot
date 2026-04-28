"""Regression tests for checker skip metadata."""

import importlib
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

    def test_dashumanhua_skip_only_turns_on_in_github_actions(self) -> None:
        with patch.dict(os.environ, {}, clear=True):
            local_module = importlib.reload(checker_tests)
            local_test = local_module.TestCheckers.test_dashumanhua_checker
            self.assertFalse(getattr(local_test, "__unittest_skip__", False))

        with patch.dict(os.environ, {"GITHUB_ACTIONS": "true"}, clear=True):
            github_module = importlib.reload(checker_tests)
            github_test = github_module.TestCheckers.test_dashumanhua_checker
            self.assertTrue(getattr(github_test, "__unittest_skip__", False))
            self.assertEqual(
                getattr(github_test, "__unittest_skip_why__", ""),
                "Validation 2026-04: site access is restricted in GitHub Actions",
            )

        importlib.reload(checker_tests)

    def test_other_recently_reviewed_sites_remain_enabled_by_default(self) -> None:
        locally_enabled = (
            "test_asurascans_integration",
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
