"""Shared title filters for Bilibili checkers."""

import re

from chinese_converter import to_simplified

# Promo/preview uploads, not episodes: PV (promo video), 迷你动画 (mini-anime
# shorts), 先行图 (preview stills). Titles are simplified before matching so
# traditional variants (先行圖) hit too; 先行図 is Japanese shinjitai, which
# to_simplified leaves alone.
NOISE_TITLE_KEYWORDS = ("迷你动画", "先行图", "先行図")
# `pv` must not be part of a longer latin word (PVP, PV数 is fine to match).
NOISE_TITLE_PATTERNS = (re.compile(r"(?<![a-z])pv(?![a-z])"),)


def is_noise_title(title: str) -> bool:
    """True when a video title marks promo/preview content instead of an episode."""
    normalized = to_simplified(str(title or "")).lower()
    if any(keyword in normalized for keyword in NOISE_TITLE_KEYWORDS):
        return True
    return any(pattern.search(normalized) for pattern in NOISE_TITLE_PATTERNS)
