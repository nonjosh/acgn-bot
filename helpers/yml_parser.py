"""YML Parser"""
import yaml
import requests
from helpers.utils import DEFAULT_HEADERS, DEFAULT_REQUEST_TIMEOUT, get_logger

logger = get_logger(__name__)


class YmlParser:
    """YmlParser"""

    def __init__(
        self,
        yml_filepath: str = None,
        yml_url: str = None,
    ) -> None:
        if yml_url:
            # Download yaml file from url if specified
            yml_text = requests.get(
                yml_url,
                headers=DEFAULT_HEADERS,
                timeout=DEFAULT_REQUEST_TIMEOUT,
            ).text
            self.yml_data = yaml.load(yml_text, Loader=yaml.FullLoader)
            logger.info("Yaml file downloaded from %s", yml_url)
        elif yml_filepath:
            # Read yaml file from file path if specified
            with open(yml_filepath, encoding="utf8") as yml_file:
                self.yml_data = yaml.load(yml_file, Loader=yaml.FullLoader)
            logger.info("Yaml file loaded from %s", yml_filepath)
        else:
            # Raise error if no yml url or file path specified
            raise ValueError("yml_url or yml_filepath must be specified")
