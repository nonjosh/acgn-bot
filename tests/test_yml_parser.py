"""Testing YML Parser class"""
import unittest
from helpers.yml_parser import YmlParser


class TestFileParser(unittest.TestCase):
    """Test file parser"""

    def test_read_list(self) -> None:
        """Read list from file"""
        # Initialize parser
        file_path = "config/list.yaml"
        yml_parser = YmlParser(yml_filepath=file_path)

        # Check if return a list
        self.assertIsInstance(yml_parser.yml_data, list)

        # Check if the list is not empty
        self.assertGreater(len(yml_parser.yml_data), 0)


# Check if can read list from url1
class TestUrlParser(unittest.TestCase):
    """Test url parser"""

    def test_read_list(self) -> None:
        """Read list from url"""
        # Initialize parser
        url = "https://raw.githubusercontent.com/nonjosh/acgn-bot/master/config/list.yaml"

        yml_parser = YmlParser(yml_url=url)

        # Check if return a list
        self.assertIsInstance(yml_parser.yml_data, list)

        # Check if the list is not empty
        self.assertGreater(len(yml_parser.yml_data), 0)
