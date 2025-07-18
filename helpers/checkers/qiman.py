import json
import time
from typing import List
from urllib.parse import urlparse, urlunparse

from helpers.chapter import Chapter
from helpers.checkers.base import AbstractChapterChecker


class QimanChecker(AbstractChapterChecker):
    """QimanChecker"""

    URL_SUBSTRING = "qmanwu2"

    def get_latest_chapter_list(self) -> List[Chapter]:
        """Get latest chapter list from qiman

        Returns:
            List[Chapter]: latest chapter list
        """
        # Update last check time
        self.last_check_time = time.strftime("%Y-%m-%dT%H:%M:%S%z")

        # Construct api url
        url_parse = urlparse(self.check_url)
        api_url = urlunparse(url_parse._replace(path="/bookchapter/"))

        comic_id = int(urlparse(self.check_url).path.strip("/"))

        try:
            # Send with POST method
            response = self.get_latest_post_response(
                url=api_url, data={"id": comic_id, "id2": 1}
            )
            """Sample response:
            [
                {
                    "id": "886859",
                    "name": "周刊136话"
                },
                {
                    "id": "886858",
                    "name": "周刊135话"
                },
                {
                    "id": "886857",
                    "name": "周刊134话"
                },
                ...
            ]
            """
            chapter_list = []
            for chapter_obj in response.json():
                chapter_id = chapter_obj["id"]
                chapter_url = urlunparse(
                    url_parse._replace(path=f"/{comic_id}/{chapter_id}.html")
                )
                chapter_list.append(Chapter(title=chapter_obj["name"], url=chapter_url))
            return chapter_list[::-1]
        except AttributeError:
            return []
        except json.decoder.JSONDecodeError:
            return []
