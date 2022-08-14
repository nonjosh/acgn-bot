import unittest
import helpers.ymlParser

# Check if can read list from file
class TestFileParser(unittest.TestCase):
    """Test file parser"""

    def test_read_list(self):
        """Read list from file"""
        # Initialize parser
        file_path = "config/list.yaml"
        yml_parser = helpers.ymlParser.YmlParser(yml_filepath=file_path)

        # Check if return a list
        self.assertIsInstance(yml_parser.yml_data, list)

        # Check if the list is not empty
        self.assertGreater(len(yml_parser.yml_data), 0)


# Check if can read list from url1
class TestUrlParser(unittest.TestCase):
    """Test url parser"""

    def test_read_list(self):
        """Read list from url"""
        # Initialize parser
        url = "https://gist.githubusercontent.com/nonjosh/99ce83987637c7b2555db659905f88f1/raw/d3f754f34d23a191acdf71297b8212721fd6e2a3/acgn_list.yml"
        yml_parser = helpers.ymlParser.YmlParser(yml_url=url)

        # Check if return a list
        self.assertIsInstance(yml_parser.yml_data, list)

        # Check if the list is not empty
        self.assertGreater(len(yml_parser.yml_data), 0)
