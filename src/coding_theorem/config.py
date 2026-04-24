"""Defaults shared across the installer (MCP URL, markers, message strings)."""

from __future__ import annotations

MCP_URL_DEFAULT = "https://theseus.travisgilbert.me/mcp"

# Identifier for managed content across markers, comments, and marker keys.
MANAGED_MARK = "coding-theorem"

# Markdown/HTML comment fences wrapping the assistant-hint block in CLAUDE.md.
BLOCK_START = f"<!-- {MANAGED_MARK} install: start -->"
BLOCK_END = f"<!-- {MANAGED_MARK} install: end -->"

# Substring embedded in any hook command we install, so uninstall can identify it.
HOOK_MARKER = f"{MANAGED_MARK}:"

# Stable MCP server key in Claude Code's settings.json. Uninstall removes this key.
MCP_SERVER_NAME = "theseus"

# Pre-search reminder that Claude Code echoes on Grep / Glob tool use. Also the
# string the README asks users to grep for as a post-install manual check.
PRE_SEARCH_MESSAGE = (
    f"{MANAGED_MARK}: use theseus_code_minimal_context(task) before searching raw files"
)
