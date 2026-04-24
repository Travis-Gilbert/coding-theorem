"""Platform base class. Concrete platforms (claude_code, future cursor, etc.) subclass this."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class PlannedChange:
    """One file-level change. Printed in --dry-run and attached to install/uninstall results."""

    target_path: str
    description: str
    diff: str = ""


@dataclass
class InstallResult:
    platform: str
    mcp_url: str
    changes: list[PlannedChange] = field(default_factory=list)
    dry_run: bool = False


@dataclass
class UninstallResult:
    platform: str
    changes: list[PlannedChange] = field(default_factory=list)
    dry_run: bool = False


@dataclass
class StatusReport:
    platform: str
    available: bool
    installed: bool
    mcp_url: str | None
    notes: list[str] = field(default_factory=list)


class Platform:
    """Install / uninstall / status lifecycle for a single coding tool."""

    name: str = ""

    def is_available(self) -> bool:
        """True when the platform's config directory exists on this machine."""
        raise NotImplementedError

    def install(self, mcp_url: str, *, dry_run: bool = False) -> InstallResult:
        raise NotImplementedError

    def uninstall(self, *, dry_run: bool = False) -> UninstallResult:
        raise NotImplementedError

    def status(self) -> StatusReport:
        raise NotImplementedError
