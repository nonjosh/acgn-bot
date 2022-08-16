import unittest
from helpers import NovelChapterHelper, ComicChapterHelper, Chapter
from main import job


class TestJob(unittest.TestCase):
    """Test job"""

    def test_comic_chapter_list_change(self):
        """Test if can get chapter list change in ComicChapterHelper"""
        # Initialize helper
        my_helper = ComicChapterHelper(
            name="test",
            urls=["http://qiman57.com/24583/"],
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

        # Test case of 1 new chapter at the end, and remove 1 chapter at the beginning
        # Remove last chapter in current chapter list
        my_helper.checker.chapter_list.pop()
        # Add 1 chapter at the beginning
        new_chapter = Chapter(title="test", url="https://www.google.com/")
        my_helper.checker.chapter_list.insert(0, new_chapter)
        updated_chapter_list = my_helper.checker.get_updated_chapter_list()
        self.assertEqual(len(updated_chapter_list), 1)

    def test_novel_chapter_list_change(self):
        """Test if can get chapter list change in NovelChapterHelper"""
        # Initialize helper
        my_helper = NovelChapterHelper(
            name="test",
            urls=["http://www.wutuxs.com/html/9/9715/"],
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

        # Test case of 1 new chapter at the end, and remove 1 chapter at the beginning
        # Remove last chapter in current chapter list
        my_helper.checker.chapter_list.pop()
        # Add 1 chapter at the beginning
        new_chapter = Chapter(title="test", url="https://www.google.com/")
        my_helper.checker.chapter_list.insert(0, new_chapter)
        updated_chapter_list = my_helper.checker.get_updated_chapter_list()
        self.assertEqual(len(updated_chapter_list), 1)
