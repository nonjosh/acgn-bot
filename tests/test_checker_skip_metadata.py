"""Regression tests for checker skip metadata."""

import unittest

import tests.test_checkers as checker_tests


class TestCheckerSkipMetadata(unittest.TestCase):
    """Ensure known-invalid checker tests have explicit skip reasons."""

    def test_known_invalid_sites_have_explicit_skip_reasons(self) -> None:
        expected_skips = {
            "test_asurascans_integration": "Validation 2026-04: site unavailable in automated tests",
            "test_dashumanhua_checker": "Validation 2026-04: site access is restricted in automated tests",
            "test_jmanga_checker": "Validation 2026-04: site unavailable in automated tests",
            "test_pickmeupgacha_checker": "Validation 2026-04: site unavailable in automated tests",
            "test_weixin_checker": "Validation 2026-04: endpoint unavailable in automated tests",
            "test_xbiquge_checker": "Validation 2026-04: site timed out in automated tests",
        }

        for test_name, reason in expected_skips.items():
            with self.subTest(test_name=test_name):
                test_method = getattr(checker_tests.TestCheckers, test_name)
                self.assertTrue(getattr(test_method, "__unittest_skip__", False))
                self.assertEqual(getattr(test_method, "__unittest_skip_why__", ""), reason)


if __name__ == "__main__":
    unittest.main()
