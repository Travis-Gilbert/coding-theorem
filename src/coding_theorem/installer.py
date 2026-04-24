"""Install / uninstall / status dispatch across one or more platforms."""

from __future__ import annotations

from dataclasses import dataclass, field

from coding_theorem.config import MCP_URL_DEFAULT
from coding_theorem.platforms import (
    InstallResult,
    Platform,
    StatusReport,
    UninstallResult,
    get_platform,
    list_platforms,
)


@dataclass
class AggregateResult:
    mcp_url: str
    installs: list[InstallResult] = field(default_factory=list)
    uninstalls: list[UninstallResult] = field(default_factory=list)
    statuses: list[StatusReport] = field(default_factory=list)
    dry_run: bool = False


def _select_platforms(platform: str | None) -> list[Platform]:
    if platform is None:
        return [p for p in list_platforms() if p.is_available()]
    return [get_platform(platform)]


def install(
    *,
    platform: str | None = None,
    mcp_url: str = MCP_URL_DEFAULT,
    dry_run: bool = False,
) -> AggregateResult:
    platforms = _select_platforms(platform)
    result = AggregateResult(mcp_url=mcp_url, dry_run=dry_run)
    for p in platforms:
        result.installs.append(p.install(mcp_url, dry_run=dry_run))
    return result


def uninstall(
    *,
    platform: str | None = None,
    dry_run: bool = False,
) -> AggregateResult:
    platforms = _select_platforms(platform)
    result = AggregateResult(mcp_url="", dry_run=dry_run)
    for p in platforms:
        result.uninstalls.append(p.uninstall(dry_run=dry_run))
    return result


def status(*, platform: str | None = None) -> AggregateResult:
    # Status always surveys every registered platform by default, installed or not.
    platforms = list_platforms() if platform is None else [get_platform(platform)]
    result = AggregateResult(mcp_url="")
    for p in platforms:
        result.statuses.append(p.status())
    return result


__all__ = ["AggregateResult", "install", "status", "uninstall"]
