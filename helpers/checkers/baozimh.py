import hashlib
import re
import time
from typing import List
from urllib.parse import urljoin, urlparse, urlunparse

import requests
from bs4.element import Tag
from chinese_converter import to_simplified

from helpers.chapter import Chapter
from helpers.checkers.base import AbstractChapterChecker
from helpers.utils import get_logger

logger = get_logger(__name__)

# baozimh.com fronts the site with a JS proof-of-work gatekeeper: solve
# SHA-256(prefix + challenge id + ":" + nonce) with N leading zero bits, then
# POST the nonce to get a 1h clearance cookie.
GATEKEEPER_POW_PREFIX = "gatekeeper-pow-v1:"
GATEKEEPER_CLEARANCE_TTL = 50 * 60


def leading_zero_bits(data: bytes) -> int:
    """Count leading zero bits in bytes."""
    bits = 0
    for byte in data:
        for bit in range(7, -1, -1):
            if (byte >> bit) & 1:
                return bits
            bits += 1
    return bits


class BaozimhChecker(AbstractChapterChecker):
    """Baozimh checker"""

    URL_SUBSTRING = "baozimh.com"

    def __init__(self, check_url: str) -> None:
        super().__init__(check_url)
        self.gatekeeper_refreshed_at = 0.0

    def get_latest_soup(self, apparent_encoding: bool = True):
        """Get latest soup, passing the gatekeeper challenge first."""
        if time.time() - self.gatekeeper_refreshed_at > GATEKEEPER_CLEARANCE_TTL:
            self.pass_gatekeeper()
        return super().get_latest_soup(apparent_encoding=apparent_encoding)

    def pass_gatekeeper(self) -> None:
        """Solve the gatekeeper challenge and store its cookies for later fetches."""
        session = requests.Session()
        session.headers.update(self.headers)

        response = session.get(self.check_url, timeout=self.request_timeout)
        if response.status_code == 200:
            self.gatekeeper_refreshed_at = time.time()
            return

        try:
            challenge_url = response.json()["challenge_url"]
            challenge_page = session.get(
                urljoin(self.check_url, challenge_url),
                timeout=self.request_timeout,
            )
            challenge_id = re.search(
                r'challengeId:"([^"]+)"', challenge_page.text
            ).group(1)
            ticket = re.search(r'ticket:"([^"]+)"', challenge_page.text).group(1)
            verify_url = re.search(
                r'verifyUrl:"([^"]+)"', challenge_page.text
            ).group(1)
            difficulty_bits = int(
                re.search(r"difficultyBits:(\d+)", challenge_page.text).group(1)
            )
        except (AttributeError, KeyError, TypeError, ValueError) as err:
            logger.warning("Cannot read baozimh gatekeeper challenge: %s", err)
            return

        nonce = self.solve_gatekeeper(challenge_id, difficulty_bits)
        verify_response = session.post(
            urljoin(self.check_url, verify_url),
            json={
                "challenge_id": challenge_id,
                "ticket": ticket,
                "nonce": nonce,
            },
            headers={"Origin": "https://www.baozimh.com", "Referer": self.check_url},
            timeout=self.request_timeout,
        )
        if verify_response.status_code != 200:
            logger.warning(
                "baozimh gatekeeper verify failed: %s", verify_response.status_code
            )
            return

        self.headers["Cookie"] = "; ".join(
            f"{cookie.name}={cookie.value}" for cookie in session.cookies
        )
        self.gatekeeper_refreshed_at = time.time()

    @staticmethod
    def solve_gatekeeper(challenge_id: str, difficulty_bits: int) -> str:
        """Find a nonce whose SHA-256 has enough leading zero bits."""
        prefix = f"{GATEKEEPER_POW_PREFIX}{challenge_id}:"
        nonce = 0
        while True:
            digest = hashlib.sha256(f"{prefix}{nonce}".encode()).digest()
            if leading_zero_bits(digest) >= difficulty_bits:
                return str(nonce)
            nonce += 1

    def get_latest_chapter_list(self) -> List[Chapter]:
        """Get latest chapter list from baozimh

        Returns:
            List[Chapter]: latest chapter list
        """
        soup = self.get_latest_soup(apparent_encoding=False)
        if soup is None:
            return []

        pure_g_div_list: List[Tag] = soup.find_all("div", {"class": "pure-g"})

        # Find which div contains chapter items
        for pure_g_div in pure_g_div_list:
            chapter_links = pure_g_div.find_all("a", {"class": "comics-chapters__item"})
            if chapter_links:
                chapter_list = []
                for link in chapter_links:
                    chapter_title = to_simplified(link.text)
                    chapter_path = link["href"]
                    chapter_url = urlunparse(
                        urlparse(self.check_url)._replace(path=chapter_path)
                    )
                    chapter_list.append(Chapter(title=chapter_title, url=chapter_url))

                # Titles are numbered (第47話); pad digits so 第47 sorts after 第9
                chapter_list.sort(
                    key=lambda c: re.sub(r"\d+", lambda m: m.group().zfill(6), c.title)
                )
                return chapter_list
        return []
