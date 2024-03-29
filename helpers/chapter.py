"""Basic chapter class"""


class Chapter:
    """Chapter class"""

    def __init__(self, title, url) -> None:
        self.title = title
        self.url = url

    def __repr__(self) -> str:
        return repr((self.url, self.title))

    def __eq__(self, other) -> bool:
        if isinstance(other, Chapter):
            return (self.title == other.title) and (self.url == other.url)
        return False

    def __ne__(self, other) -> bool:
        return not self.__eq__(other)

    def __hash__(self) -> int:
        return hash(self.__repr__())
