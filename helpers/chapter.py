"""Basic chapter class"""


class Chapter:
    """Chapter class"""

    def __init__(self, title, url) -> None:
        self.title = title
        self.url = url

    def __repr__(self):
        return repr((self.url, self.title))
