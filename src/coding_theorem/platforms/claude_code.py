"""Claude Code platform. Manages ~/.claude/settings.json and ~/.claude/CLAUDE.md."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from coding_theorem.config import (
    BLOCK_END,
    BLOCK_START,
    HOOK_MARKER,
    MANAGED_MARK,
    MCP_SERVER_NAME,
    PRE_SEARCH_MESSAGE,
)
from coding_theorem.platforms.base import (
    InstallResult,
    PlannedChange,
    Platform,
    StatusReport,
    UninstallResult,
)


class ClaudeCodePlatform(Platform):
    """Claude Code (claude.ai/code).

    Touches two files under ~/.claude/:
      settings.json: adds mcpServers.theseus and a PreToolUse hook whose command echoes
        PRE_SEARCH_MESSAGE on Grep and Glob.
      CLAUDE.md: writes a managed block (fenced by BLOCK_START / BLOCK_END) with assistant
        hints pointing at the Theseus tools.
    """

    name = "claude-code"

    @property
    def config_dir(self) -> Path:
        return Path.home() / ".claude"

    @property
    def settings_path(self) -> Path:
        return self.config_dir / "settings.json"

    @property
    def instructions_path(self) -> Path:
        return self.config_dir / "CLAUDE.md"

    def is_available(self) -> bool:
        return self.config_dir.exists()

    def install(self, mcp_url: str, *, dry_run: bool = False) -> InstallResult:
        changes: list[PlannedChange] = []

        settings_before = _read_json(self.settings_path)
        settings_after = _apply_settings(settings_before, mcp_url)
        if settings_before != settings_after:
            changes.append(
                PlannedChange(
                    target_path=str(self.settings_path),
                    description=(
                        f"register MCP server '{MCP_SERVER_NAME}' and install PreToolUse hook"
                    ),
                    diff=_json_diff(settings_before, settings_after),
                )
            )
            if not dry_run:
                _write_json(self.settings_path, settings_after)

        claude_md_before = _read_text(self.instructions_path)
        claude_md_after = _apply_managed_block(claude_md_before, _render_instructions(mcp_url))
        if claude_md_before != claude_md_after:
            changes.append(
                PlannedChange(
                    target_path=str(self.instructions_path),
                    description="write coding-theorem managed block with Theseus tool hints",
                )
            )
            if not dry_run:
                _write_text(self.instructions_path, claude_md_after)

        return InstallResult(platform=self.name, mcp_url=mcp_url, changes=changes, dry_run=dry_run)

    def uninstall(self, *, dry_run: bool = False) -> UninstallResult:
        changes: list[PlannedChange] = []

        settings_before = _read_json(self.settings_path)
        settings_after = _strip_settings(settings_before)
        if settings_before != settings_after:
            changes.append(
                PlannedChange(
                    target_path=str(self.settings_path),
                    description=(f"remove MCP server '{MCP_SERVER_NAME}' and coding-theorem hook"),
                )
            )
            if not dry_run:
                _write_json(self.settings_path, settings_after)

        claude_md_before = _read_text(self.instructions_path)
        claude_md_after = _strip_managed_block(claude_md_before)
        if claude_md_before != claude_md_after:
            changes.append(
                PlannedChange(
                    target_path=str(self.instructions_path),
                    description="remove coding-theorem managed block",
                )
            )
            if not dry_run:
                _write_text(self.instructions_path, claude_md_after)

        return UninstallResult(platform=self.name, changes=changes, dry_run=dry_run)

    def status(self) -> StatusReport:
        available = self.is_available()
        settings = _read_json(self.settings_path)
        mcp_url = settings.get("mcpServers", {}).get(MCP_SERVER_NAME, {}).get("url")
        hook_installed = _has_managed_hook(settings)
        block_present = BLOCK_START in _read_text(self.instructions_path)
        installed = bool(mcp_url) or hook_installed or block_present

        notes: list[str] = []
        if mcp_url:
            notes.append(f"MCP server '{MCP_SERVER_NAME}' configured at {mcp_url}")
        if hook_installed:
            notes.append("PreToolUse hook installed")
        if block_present:
            notes.append("CLAUDE.md managed block present")
        if not available:
            notes.append(f"Claude Code config directory not found at {self.config_dir}")

        return StatusReport(
            platform=self.name,
            available=available,
            installed=installed,
            mcp_url=mcp_url,
            notes=notes,
        )


# -- internal helpers -----------------------------------------------------------


def _read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError):
        return {}
    return data if isinstance(data, dict) else {}


def _write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def _read_text(path: Path) -> str:
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8")


def _write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _apply_settings(settings: dict[str, Any], mcp_url: str) -> dict[str, Any]:
    out: dict[str, Any] = json.loads(json.dumps(settings))

    mcp_servers = out.setdefault("mcpServers", {})
    mcp_servers[MCP_SERVER_NAME] = {
        "type": "http",
        "url": mcp_url,
        "description": f"Theseus knowledge graph ({MANAGED_MARK})",
    }

    hooks = out.setdefault("hooks", {})
    pre_tool_use = hooks.setdefault("PreToolUse", [])
    pre_tool_use[:] = [entry for entry in pre_tool_use if not _is_managed_hook_entry(entry)]
    pre_tool_use.append(
        {
            "matcher": "Grep|Glob",
            "hooks": [
                {
                    "type": "command",
                    "command": f"echo '{PRE_SEARCH_MESSAGE}'",
                }
            ],
        }
    )
    return out


def _strip_settings(settings: dict[str, Any]) -> dict[str, Any]:
    out: dict[str, Any] = json.loads(json.dumps(settings))
    if "mcpServers" in out:
        out["mcpServers"].pop(MCP_SERVER_NAME, None)
        if not out["mcpServers"]:
            out.pop("mcpServers")
    if "hooks" in out and "PreToolUse" in out["hooks"]:
        out["hooks"]["PreToolUse"] = [
            entry for entry in out["hooks"]["PreToolUse"] if not _is_managed_hook_entry(entry)
        ]
        if not out["hooks"]["PreToolUse"]:
            out["hooks"].pop("PreToolUse")
        if not out["hooks"]:
            out.pop("hooks")
    return out


def _is_managed_hook_entry(entry: dict[str, Any]) -> bool:
    for hook in entry.get("hooks", []):
        cmd = hook.get("command", "")
        if HOOK_MARKER in cmd:
            return True
    return False


def _has_managed_hook(settings: dict[str, Any]) -> bool:
    for entry in settings.get("hooks", {}).get("PreToolUse", []):
        if _is_managed_hook_entry(entry):
            return True
    return False


def _apply_managed_block(current: str, block_body: str) -> str:
    new_block = f"{BLOCK_START}\n{block_body}\n{BLOCK_END}"
    if BLOCK_START in current and BLOCK_END in current:
        start = current.index(BLOCK_START)
        end = current.index(BLOCK_END) + len(BLOCK_END)
        return current[:start] + new_block + current[end:]
    if not current:
        return new_block + "\n"
    separator = "" if current.endswith("\n\n") else ("\n" if current.endswith("\n") else "\n\n")
    return current + separator + new_block + "\n"


def _strip_managed_block(current: str) -> str:
    if BLOCK_START not in current or BLOCK_END not in current:
        return current
    start = current.index(BLOCK_START)
    end = current.index(BLOCK_END) + len(BLOCK_END)
    head = current[:start]
    tail = current[end:]
    if tail.startswith("\n"):
        tail = tail[1:]
    if head.endswith("\n\n"):
        head = head[:-1]
    return head + tail


def _render_instructions(mcp_url: str) -> str:
    return (
        "## Theseus MCP tools\n"
        "\n"
        f"A Theseus MCP server is available at `{mcp_url}`. Before searching raw files with "
        "Grep or Glob, call `theseus_code_minimal_context(task)` to fetch the graph's view of "
        "the relevant code, concepts, and decisions. Use `theseus_code_explain`, "
        "`theseus_find_connections`, and `theseus_code_impact` for deeper queries.\n"
        "\n"
        f"Managed by `{MANAGED_MARK}`. Run `coding-theorem uninstall` to remove this block."
    )


def _json_diff(before: dict[str, Any], after: dict[str, Any]) -> str:
    if before == after:
        return ""
    before_s = json.dumps(before, indent=2, sort_keys=True)
    after_s = json.dumps(after, indent=2, sort_keys=True)
    return f"--- before\n{before_s}\n+++ after\n{after_s}"
