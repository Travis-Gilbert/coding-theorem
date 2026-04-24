"""coding-theorem: installs the Theseus MCP server into local coding tools."""

from __future__ import annotations

__version__ = "0.1.0"

from coding_theorem.installer import AggregateResult, install, status, uninstall

__all__ = ["AggregateResult", "__version__", "install", "status", "uninstall"]
