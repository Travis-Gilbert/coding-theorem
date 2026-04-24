"""Tests for the install / uninstall / status lifecycle."""

from __future__ import annotations

import json
from pathlib import Path

from coding_theorem.config import BLOCK_END, BLOCK_START, MCP_SERVER_NAME
from coding_theorem.installer import install, status, uninstall


def _claude_md(fake_home: Path) -> Path:
    return fake_home / ".claude" / "CLAUDE.md"


def _settings(fake_home: Path) -> Path:
    return fake_home / ".claude" / "settings.json"


def test_install_writes_managed_block(fake_config_dir: Path) -> None:
    install(platform="claude-code")
    content = _claude_md(fake_config_dir).read_text(encoding="utf-8")
    assert BLOCK_START in content
    assert BLOCK_END in content


def test_install_twice_replaces_not_duplicates(fake_config_dir: Path) -> None:
    install(platform="claude-code")
    install(platform="claude-code")
    content = _claude_md(fake_config_dir).read_text(encoding="utf-8")
    assert content.count(BLOCK_START) == 1
    assert content.count(BLOCK_END) == 1


def test_uninstall_preserves_surrounding_content(fake_config_dir: Path) -> None:
    claude_md = _claude_md(fake_config_dir)
    claude_md.parent.mkdir(parents=True, exist_ok=True)
    claude_md.write_text("# My Notes\n\nSome pre-existing content.\n", encoding="utf-8")

    install(platform="claude-code")
    uninstall(platform="claude-code")

    content = claude_md.read_text(encoding="utf-8")
    assert "My Notes" in content
    assert "Some pre-existing content." in content
    assert BLOCK_START not in content
    assert BLOCK_END not in content


def test_status_reports_platform_and_mcp_url(fake_config_dir: Path) -> None:
    install(platform="claude-code", mcp_url="https://example.com/mcp")
    result = status(platform="claude-code")
    assert len(result.statuses) == 1
    report = result.statuses[0]
    assert report.platform == "claude-code"
    assert report.installed is True
    assert report.mcp_url == "https://example.com/mcp"


def test_install_dry_run_writes_nothing(fake_config_dir: Path) -> None:
    fake_config_dir.joinpath(".claude").mkdir(parents=True, exist_ok=True)
    result = install(platform="claude-code", dry_run=True)

    assert result.dry_run is True
    assert result.installs and result.installs[0].changes
    assert not _settings(fake_config_dir).exists()
    assert not _claude_md(fake_config_dir).exists()


def test_install_settings_registers_mcp_server_and_hook(fake_config_dir: Path) -> None:
    install(platform="claude-code", mcp_url="https://example.com/mcp")
    settings = json.loads(_settings(fake_config_dir).read_text(encoding="utf-8"))

    assert MCP_SERVER_NAME in settings["mcpServers"]
    assert settings["mcpServers"][MCP_SERVER_NAME]["url"] == "https://example.com/mcp"

    commands = [
        hook["command"] for entry in settings["hooks"]["PreToolUse"] for hook in entry["hooks"]
    ]
    assert any("coding-theorem:" in cmd for cmd in commands)


def test_uninstall_removes_mcp_server_and_hook(fake_config_dir: Path) -> None:
    install(platform="claude-code")
    uninstall(platform="claude-code")

    settings_path = _settings(fake_config_dir)
    if settings_path.exists():
        settings = json.loads(settings_path.read_text(encoding="utf-8"))
        assert MCP_SERVER_NAME not in settings.get("mcpServers", {})
        assert not any(
            "coding-theorem:" in hook.get("command", "")
            for entry in settings.get("hooks", {}).get("PreToolUse", [])
            for hook in entry.get("hooks", [])
        )
