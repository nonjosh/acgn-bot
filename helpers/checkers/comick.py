"""Checker for comick.live comic pages and chapter list API."""

from datetime import datetime
from typing import Dict, Iterable, List, Optional, Tuple
from urllib.parse import urlparse, urlunparse

from helpers.chapter import Chapter
from helpers.checkers.base import AbstractChapterChecker


class ComickChecker(AbstractChapterChecker):
    """Comick.live checker

    Expects a comic page URL like:
        https://comick.live/comic/<slug>

    Will construct API URL:
        https://comick.live/api/comics/<slug>/chapter-list
    """

    URL_SUBSTRING = "comick.live"

    @staticmethod
    def _parse_ts(ts: Optional[str]) -> Optional[datetime]:
        if not ts:
            return None
        try:
            # Make Zulu time ISO compatible for fromisoformat
            return datetime.fromisoformat(ts.replace("Z", "+00:00"))
        except Exception:  # pylint: disable=broad-except
            return None

    @staticmethod
    def _item_rank(it: dict) -> Tuple[int, Optional[datetime], Optional[datetime], int]:
        # Higher is newer: prefer updated_at, then created_at, then id
        upd = ComickChecker._parse_ts(it.get("updated_at"))
        crt = ComickChecker._parse_ts(it.get("created_at"))
        try:
            iid = int(it.get("id")) if it.get("id") is not None else -1
        except Exception:  # pylint: disable=broad-except
            iid = -1
        # Presence flag ensures entries with timestamps beat those without
        return (
            1 if upd else 0,
            upd or crt,
            crt,
            iid,
        )

    @staticmethod
    def _chap_sort_key(ch: str):
        try:
            return (0, float(ch))
        except Exception:  # pylint: disable=broad-except
            return (1, ch)

    def get_latest_chapter_list(self) -> List[Chapter]:
        """Get latest chapter list from comick.live

        Returns:
            List[Chapter]: latest chapter list
        """
        try:
            parsed = urlparse(self.check_url)
            segments = parsed.path.strip("/").split("/")
            # Expecting ["comic", <slug>] or ["comic", <slug>, ...]
            if len(segments) < 2 or segments[0] != "comic":
                return []
            slug = segments[1]

            api_url = urlunparse(
                parsed._replace(path=f"/api/comics/{slug}/chapter-list")
            )
            response = self.get_latest_response(url=api_url, apparent_encoding=False)
            if response is None:
                return []

            # Response example (abridged):
            # Example: {"data": [{"hid": "...", "chap": "282", "title": "", ...}, ...]}
            payload = response.json()
            data: Iterable[dict] = (
                payload.get("data", []) if isinstance(payload, dict) else []
            )

            # Deduplicate by chapter number, keeping the newest entry
            best_by_chap: Dict[str, dict] = {}
            for it in data:
                chap = it.get("chap")
                chap_key = str(chap) if chap is not None else None
                if not chap_key:
                    # Skip items without a chapter identifier
                    continue
                if chap_key not in best_by_chap:
                    best_by_chap[chap_key] = it
                else:
                    if ComickChecker._item_rank(it) > ComickChecker._item_rank(
                        best_by_chap[chap_key]
                    ):
                        best_by_chap[chap_key] = it

            # Sort chapters in ascending numeric order when possible
            result: List[Chapter] = []
            for chap_key in sorted(best_by_chap, key=ComickChecker._chap_sort_key):
                chosen = best_by_chap[chap_key]
                if not chosen.get("hid"):
                    continue  # Can't construct a chapter URL without HID
                lang = (chosen.get("lang") or "en").lower()
                result.append(
                    Chapter(
                        title=f"Ch.{chap_key} {(chosen.get('title') or '')}".strip(),
                        url=urlunparse(
                            parsed._replace(
                                path=(
                                    f"/comic/{slug}/"
                                    f"{chosen.get('hid')}-chapter-{chap_key}-{lang}"
                                )
                            )
                        ),
                    )
                )

            return result
        except Exception:  # pylint: disable=broad-except
            return []
