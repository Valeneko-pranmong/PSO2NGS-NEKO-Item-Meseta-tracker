from __future__ import annotations

import re
from typing import Dict, List, Optional, Tuple, Union


def format_compact(value: Union[int, float]) -> str:
    """
    Format numeric value into compact readable string (e.g. 1.25M, 15.0k, 500).
    """
    av = abs(value)
    sign = "-" if value < 0 else ""
    if av >= 1_000_000:
        return f"{sign}{av / 1_000_000:.2f}M"
    if av >= 10_000:
        return f"{sign}{av / 1_000:.1f}k"
    return f"{sign}{int(av):,}"


def format_rate(meseta_per_hour: float) -> str:
    """
    Format hourly rate in Meseta/hr.
    """
    if meseta_per_hour <= 0:
        return "0 /hr"
    if meseta_per_hour >= 1_000_000:
        return f"{meseta_per_hour / 1_000_000:.2f} M/hr"
    if meseta_per_hour >= 1_000:
        return f"{meseta_per_hour / 1_000:.1f} k/hr"
    return f"{int(meseta_per_hour)} /hr"


def format_duration(seconds: float) -> str:
    """
    Format elapsed seconds into HH:MM:SS string.
    """
    if seconds < 0:
        seconds = 0
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    return f"{h:02d}:{m:02d}:{s:02d}"


def filter_and_sort_items(
    item_counts: Dict[str, int],
    watchlist: Optional[List[str]] = None,
    keyword: Optional[str] = None,
    filter_enabled: bool = False,
    max_items: int = 50,
) -> List[Tuple[str, int]]:
    """
    Filter item counts by watchlist and keyword, then return top items sorted by count descending.
    """
    if filter_enabled:
        if watchlist:
            wl_lower = [w.strip().lower() for w in watchlist if w.strip()]
            if wl_lower:
                filtered = {
                    k: v for k, v in item_counts.items()
                    if any(w in k.lower() for w in wl_lower)
                }
            else:
                filtered = {}
        else:
            filtered = {}
    else:
        filtered = item_counts

    if keyword:
        kw = keyword.strip().lower()
        filtered = {k: v for k, v in filtered.items() if kw in k.lower()}

    return sorted(filtered.items(), key=lambda kv: kv[1], reverse=True)[:max_items]


def extract_character_info(line: str) -> Optional[Tuple[str, str]]:
    """
    Extract (character_name, player_id) from PSO2:NGS ActionLog line.
    Format: Timestamp \t Seq \t [Action] \t PlayerID \t CharacterName \t ...
    """
    parts = line.strip().split('\t')
    if len(parts) >= 5 and parts[3].strip().isdigit():
        cname = parts[4].strip()
        if cname and not cname.startswith('[') and 'Num(' not in cname:
            return cname, parts[3].strip()
    return None
