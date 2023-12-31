"""MediaListState class for storing the state of the media list."""
from typing import List
from helpers.media import MediaHelper


class MediaListState:
    """MediaListState class for storing the state of the media list.

    Attributes:
        media_helper_list (list): list of MediaHelper objects
    """

    media_helper_list: List[MediaHelper] = []
