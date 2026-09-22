"""
NEKO Tracker Semantic Versioning & Version Security Subsystem
Canonical module providing SemVer parsing, precedence comparison,
and client version security policy gating.
"""

from __future__ import annotations

from typing import Any, Optional, Set, Tuple

try:
    from config import MIN_SECURE_VERSION, REVOKED_VERSIONS
except Exception:
    MIN_SECURE_VERSION = "7.1.0"
    REVOKED_VERSIONS = ["7.0.0-alpha", "7.0.0"]


def parse_semver(v: str) -> Tuple[int, int, int, str]:
    """Parse semantic version string into (major, minor, patch, pre_release)."""
    if not v or not isinstance(v, str):
        return (0, 0, 0, "")
    clean = v.strip().lstrip("vV").strip()
    pre = ""
    if "-" in clean:
        parts_pre = clean.split("-", 1)
        clean = parts_pre[0].strip()
        pre = parts_pre[1].strip()
    nums = clean.split(".")
    major = int(nums[0]) if len(nums) > 0 and nums[0].isdigit() else 0
    minor = int(nums[1]) if len(nums) > 1 and nums[1].isdigit() else 0
    patch = int(nums[2]) if len(nums) > 2 and nums[2].isdigit() else 0
    return (major, minor, patch, pre)


def compare_semver(v1: str, v2: str) -> int:
    """
    Compare two semantic version strings.
    Returns: -1 if v1 < v2, 0 if equal, 1 if v1 > v2.
    Pre-release versions (e.g. 7.0.0-alpha) have lower precedence than core release.
    """
    p1 = parse_semver(v1)
    p2 = parse_semver(v2)
    if p1[:3] > p2[:3]:
        return 1
    if p1[:3] < p2[:3]:
        return -1
    if p1[3] and not p2[3]:
        return -1
    if not p1[3] and p2[3]:
        return 1
    if p1[3] and p2[3]:
        if p1[3] < p2[3]:
            return -1
        if p1[3] > p2[3]:
            return 1
    return 0


def is_version_secure(
    version: str,
    min_version: str = MIN_SECURE_VERSION,
    revoked_versions: Optional[Any] = None,
) -> bool:
    """
    Verify client version against security policy.
    Rejects revoked versions (e.g. 7.0.0-alpha) and versions below MIN_SECURE_VERSION.
    """
    if not version or not isinstance(version, str):
        return False
    v_clean = version.strip().lower().lstrip("v").strip()
    target_revoked = revoked_versions if revoked_versions is not None else REVOKED_VERSIONS
    rev_set: Set[str] = {r.lower().lstrip("v").strip() for r in target_revoked}
    if v_clean in rev_set:
        return False
    return compare_semver(version, min_version) >= 0


__all__ = [
    "parse_semver",
    "compare_semver",
    "is_version_secure",
    "MIN_SECURE_VERSION",
    "REVOKED_VERSIONS",
]
