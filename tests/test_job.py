"""Test basic flow of each job"""
import unittest
from helpers.chapter import Chapter
from helpers import ChapterHelper


class TestJob(unittest.TestCase):
    """Test job"""

    def test_chapter_list_change(self) -> None:
        """Test if can get chapter list change in ChapterHelper"""
        # Initialize helper
        my_helper = ChapterHelper(
            name="test",
            urls=["http://qiman57.com/24583/"],
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
