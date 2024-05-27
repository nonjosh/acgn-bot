"""Config helper class"""
import os

from helpers.yml_parser import YmlParser

DEFAULT_LIST_YAML_PATH = "config/list.yaml"


class ConfigHelper:
    """Config helper class"""

    def __init__(self):

        # Check if CONFIG_YML_URL is set
        if "CONFIG_YML_URL" in os.environ:
            # Get config from url
            yml_url = os.environ["CONFIG_YML_URL"]
            yml_parser = YmlParser(yml_url=yml_url)
            self.yml_data = yml_parser.yml_data
        elif "CONFIG_YML_FILEPATH" in os.environ:
            # Get config from path
            yml_filepath = os.environ["CONFIG_YML_FILEPATH"]
            yml_parser = YmlParser(yml_filepath=yml_filepath)
            self.yml_data = yml_parser.yml_data
        else:
            # Get config from default path
            yml_parser = YmlParser(yml_filepath=DEFAULT_LIST_YAML_PATH)
            self.yml_data = yml_parser.yml_data

    def get_yml_data(self) -> list:
        """Get yml data"""
        return self.yml_data
