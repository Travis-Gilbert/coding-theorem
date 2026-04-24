"""Platform registry."""

from __future__ import annotations

from coding_theorem.platforms.base import (
    InstallResult,
    PlannedChange,
    Platform,
    StatusReport,
    UninstallResult,
)
from coding_theorem.platforms.claude_code import ClaudeCodePlatform

PLATFORMS: dict[str, type[Platform]] = {
    ClaudeCodePlatform.name: ClaudeCodePlatform,
}


def get_platform(name: str) -> Platform:
    if name not in PLATFORMS:
        available = ", ".join(sorted(PLATFORMS.keys())) or "(none)"
        raise KeyError(f"Unknown platform {name!r}. Available: {available}")
    return PLATFORMS[name]()


def list_platforms() -> list[Platform]:
    return [cls() for cls in PLATFORMS.values()]


__all__ = [
    "PLATFORMS",
    "InstallResult",
    "PlannedChange",
    "Platform",
    "StatusReport",
    "UninstallResult",
    "get_platform",
    "list_platforms",
]
