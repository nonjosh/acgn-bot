"""Test basic flow of each job"""

import unittest

from helpers.chapter import Chapter
from helpers.media import MediaHelper
from helpers.utils import check_url_valid, get_chapter_list_diff


class TestMediaHelper(unittest.TestCase):
    """Test MediaHelper"""

    def test_chapter_list_change(self) -> None:
        """Test if can get chapter list change in ChapterHelper"""
        url = "https://www.dashumanhua.com/comic/fangkainagenvwu/"

        if not check_url_valid(url=url):
            self.skipTest(f"{url} is not healthy")

        # Initialize helper
        my_helper = MediaHelper(
            name="大樹漫",
            urls=[url],
            media_type="comic",
        )

        # Check if can get chapter list
        updated_chapter_list = my_helper.checker.get_updated_chapter_list()
        self.assertGreater(len(updated_chapter_list), 0)

        # Test case of 1 new chapter at the end
        # Remove last chapter in current chapter list
        my_helper.checker.chapter_list.pop()
        updated_chapter_list = my_helper.checker.get_updated_chapter_list()
        self.assertEqual(len(updated_chapter_list), 1)

        # Test case of multiple new chapters at the end
        # Remove last 3 chapters in current chapter list
        my_helper.checker.chapter_list = my_helper.checker.chapter_list[:-3]
        updated_chapter_list = my_helper.checker.get_updated_chapter_list()
        self.assertEqual(len(updated_chapter_list), 3)

        # Test case of 1 new chapter at the end,
        # and remove 1 chapter at the beginning
        # Remove last chapter in current chapter list
        my_helper.checker.chapter_list.pop()
        # Add 1 chapter at the beginning
        new_chapter = Chapter(title="test", url="https://www.google.com/")
        my_helper.checker.chapter_list.insert(0, new_chapter)
        updated_chapter_list = my_helper.checker.get_updated_chapter_list()
        self.assertEqual(len(updated_chapter_list), 1)


class TestChapterListDiff(unittest.TestCase):
    """Test chapter diff edge cases."""

    def test_ignore_existing_chapter_url_rewrites(self) -> None:
        """Existing chapters should not look new when a site rewrites chapter URLs."""

        old_list = [
            Chapter(title="Chapter 1", url="https://old.example/1"),
            Chapter(title="Chapter 2", url="https://old.example/2"),
        ]
        new_list = [
            Chapter(title="Chapter 1", url="https://new.example/1"),
            Chapter(title="Chapter 2", url="https://new.example/2"),
        ]

        self.assertEqual(get_chapter_list_diff(new_list, old_list), [])

    def test_keep_only_truly_new_titles_when_urls_rewrite(self) -> None:
        """New chapters should still be detected when old chapter URLs also change."""

        old_list = [
            Chapter(title="Chapter 1", url="https://old.example/1"),
            Chapter(title="Chapter 2", url="https://old.example/2"),
        ]
        new_chapter = Chapter(title="Chapter 3", url="https://new.example/3")
        new_list = [
            Chapter(title=" Chapter   1 ", url="https://new.example/1"),
            Chapter(title="chapter 2", url="https://new.example/2"),
            new_chapter,
        ]

        self.assertEqual(get_chapter_list_diff(new_list, old_list), [new_chapter])
