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

        # Validate yaml file
        if not self.validate():
            raise ValueError("Yaml file is invalid")

    def validate(self) -> bool:
        """Validate yaml file"""

        # Check if the yaml file is a list
        if not isinstance(self.yml_data, list):
            logger.error("Yaml file is not a list")
            return False

        # Check if each item in the list contains the required keys
        for item in self.yml_data:
            if "name" not in item:
                logger.error("Yaml file item does not contain name")
                return False
            if not any(key in item for key in ("comic_urls", "novel_urls")):
                logger.error(
                    "Yaml file item does not contain comic_urls or novel_urls"
                )
                return False

        # Check if comic_urls and novel_urls are lists
        for item in self.yml_data:
            if "comic_urls" in item and not isinstance(
                item["comic_urls"], list
            ):
                logger.error("comic_urls is not a list")
                return False
            if "novel_urls" in item and not isinstance(
                item["novel_urls"], list
            ):
                logger.error("novel_urls is not a list")
                return False

        # Return true if all checks passed
        return True
