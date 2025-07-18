"""Unit tests for ManhuaguiChecker rate limiting functionality."""

import threading
import time
import unittest
from unittest.mock import MagicMock, patch

from helpers.checkers.manhuagui import ManhuaguiChecker


class TestManhuaguiRateLimiting(unittest.TestCase):
    """Test rate limiting functionality of ManhuaguiChecker"""

    def setUp(self):
        """Set up test environment"""
        # Reset class variables before each test
        ManhuaguiChecker._last_request_time = 0
        ManhuaguiChecker._min_request_interval = 30
        ManhuaguiChecker._request_lock = None

    def tearDown(self):
        """Clean up after each test"""
        # Reset class variables after each test
        ManhuaguiChecker._last_request_time = 0
        ManhuaguiChecker._min_request_interval = 30
        ManhuaguiChecker._request_lock = None

    def test_rate_limit_initialization(self):
        """Test that rate limiting variables are properly initialized"""
        checker = ManhuaguiChecker("https://m.manhuagui.com/comic/17165/")

        # Check that lock is created
        self.assertIsNotNone(ManhuaguiChecker._request_lock)
        self.assertIsInstance(ManhuaguiChecker._request_lock, threading.Lock)

        # Check default values
        self.assertEqual(ManhuaguiChecker._min_request_interval, 30)
        self.assertEqual(checker.retry_interval, 10)
        self.assertEqual(checker.max_retry_num, 2)

    def test_set_rate_limit_interval_valid(self):
        """Test setting valid rate limit interval"""
        ManhuaguiChecker.set_rate_limit_interval(60)
        self.assertEqual(ManhuaguiChecker._min_request_interval, 60)

        ManhuaguiChecker.set_rate_limit_interval(15)
        self.assertEqual(ManhuaguiChecker._min_request_interval, 15)

    def test_set_rate_limit_interval_invalid(self):
        """Test setting invalid rate limit interval"""
        original_interval = ManhuaguiChecker._min_request_interval

        # Test negative value
        ManhuaguiChecker.set_rate_limit_interval(-5)
        self.assertEqual(ManhuaguiChecker._min_request_interval, original_interval)

        # Test zero value
        ManhuaguiChecker.set_rate_limit_interval(0)
        self.assertEqual(ManhuaguiChecker._min_request_interval, original_interval)

    def test_rate_limiting_timing(self):
        """Test that rate limiting enforces correct timing"""
        # Set a short interval for testing
        ManhuaguiChecker.set_rate_limit_interval(2)

        checker = ManhuaguiChecker("https://m.manhuagui.com/comic/17165/")

        # First call should go through immediately
        start_time = time.time()
        checker._wait_for_rate_limit()
        first_call_time = time.time() - start_time

        # Should be very fast (less than 0.1 seconds)
        self.assertLess(first_call_time, 0.1)

        # Second call should be delayed
        start_time = time.time()
        checker._wait_for_rate_limit()
        second_call_time = time.time() - start_time

        # Should wait at least the rate limit interval (allowing small margin)
        self.assertGreaterEqual(second_call_time, 1.9)

    def test_rate_limiting_thread_safety(self):
        """Test that rate limiting works correctly with multiple threads"""
        ManhuaguiChecker.set_rate_limit_interval(1)  # 1 second for testing

        results = []
        start_time = time.time()

        def worker():
            checker = ManhuaguiChecker("https://m.manhuagui.com/comic/17165/")
            checker._wait_for_rate_limit()
            results.append(time.time() - start_time)

        # Create multiple threads
        threads = []
        for _ in range(3):
            thread = threading.Thread(target=worker)
            threads.append(thread)

        # Start all threads
        for thread in threads:
            thread.start()

        # Wait for all threads to complete
        for thread in threads:
            thread.join()

        # Sort results to check timing
        results.sort()

        # Should have 3 results
        self.assertEqual(len(results), 3)

        # Each request should be at least 1 second apart (allowing small margin)
        if len(results) >= 2:
            self.assertGreaterEqual(results[1] - results[0], 0.9)
        if len(results) >= 3:
            self.assertGreaterEqual(results[2] - results[1], 0.9)

    @patch("helpers.checkers.base.AbstractChapterChecker.get_latest_response")
    def test_get_latest_response_rate_limited(self, mock_super_response):
        """Test that get_latest_response applies rate limiting"""
        mock_response = MagicMock()
        mock_super_response.return_value = mock_response

        ManhuaguiChecker.set_rate_limit_interval(1)
        checker = ManhuaguiChecker("https://m.manhuagui.com/comic/17165/")

        # First call
        start_time = time.time()
        result1 = checker.get_latest_response()
        first_duration = time.time() - start_time

        # Second call should be rate limited
        start_time = time.time()
        result2 = checker.get_latest_response()
        second_duration = time.time() - start_time

        # Verify that the super method was called
        self.assertEqual(mock_super_response.call_count, 2)

        # Verify rate limiting was applied
        self.assertLess(first_duration, 0.1)  # First call should be fast
        self.assertGreaterEqual(second_duration, 0.9)  # Second call should wait

        # Verify return values
        self.assertEqual(result1, mock_response)
        self.assertEqual(result2, mock_response)

    @patch("helpers.checkers.base.AbstractChapterChecker.get_latest_post_response")
    def test_get_post_response_rate_limited(self, mock_super_post):
        """Test that get_latest_post_response applies rate limiting"""
        mock_response = MagicMock()
        mock_super_post.return_value = mock_response

        ManhuaguiChecker.set_rate_limit_interval(1)
        checker = ManhuaguiChecker("https://m.manhuagui.com/comic/17165/")

        # First call
        start_time = time.time()
        result1 = checker.get_latest_post_response()
        first_duration = time.time() - start_time

        # Second call should be rate limited
        start_time = time.time()
        result2 = checker.get_latest_post_response()
        second_duration = time.time() - start_time

        # Verify that the super method was called
        self.assertEqual(mock_super_post.call_count, 2)

        # Verify rate limiting was applied
        self.assertLess(first_duration, 0.1)  # First call should be fast
        self.assertGreaterEqual(second_duration, 0.9)  # Second call should wait

        # Verify return values
        self.assertEqual(result1, mock_response)
        self.assertEqual(result2, mock_response)

    def test_multiple_instances_share_rate_limit(self):
        """Test that multiple instances of ManhuaguiChecker share the same rate limit"""
        ManhuaguiChecker.set_rate_limit_interval(1)

        checker1 = ManhuaguiChecker("https://m.manhuagui.com/comic/17165/")
        checker2 = ManhuaguiChecker("https://m.manhuagui.com/comic/12345/")

        # First call from checker1
        start_time = time.time()
        checker1._wait_for_rate_limit()
        first_duration = time.time() - start_time

        # Second call from checker2 should still be rate limited
        start_time = time.time()
        checker2._wait_for_rate_limit()
        second_duration = time.time() - start_time

        # Verify rate limiting is shared
        self.assertLess(first_duration, 0.1)  # First call should be fast
        self.assertGreaterEqual(second_duration, 0.9)  # Second call should wait

    def test_rate_limit_after_sufficient_time(self):
        """Test that requests are not delayed if sufficient time has passed"""
        ManhuaguiChecker.set_rate_limit_interval(1)
        checker = ManhuaguiChecker("https://m.manhuagui.com/comic/17165/")

        # First call
        checker._wait_for_rate_limit()

        # Simulate waiting longer than the rate limit interval
        with patch("time.time", side_effect=[0, 1.1, 1.1, 1.2]):
            # Second call should not be delayed
            start_time = time.time()
            checker._wait_for_rate_limit()
            duration = time.time() - start_time
        # Should be fast since enough time has passed
        self.assertLess(duration, 0.1)


if __name__ == "__main__":
    unittest.main()
