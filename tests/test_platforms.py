"""Tests for platform registry and Claude Code specifics."""

from __future__ import annotations

from pathlib import Path

from coding_theorem.config import PRE_SEARCH_MESSAGE
from coding_theorem.platforms import PLATFORMS, get_platform
from coding_theorem.platforms.claude_code import ClaudeCodePlatform


def test_claude_code_targets_correct_config_path(fake_config_dir: Path) -> None:
    platform = ClaudeCodePlatform()
    assert platform.settings_path == fake_config_dir / ".claude" / "settings.json"
    assert platform.instructions_path == fake_config_dir / ".claude" / "CLAUDE.md"


def test_claude_code_install_block_contains_mcp_url_and_hint(fake_config_dir: Path) -> None:
    platform = ClaudeCodePlatform()
    platform.install("https://self-host.example.com/mcp")

    block = platform.instructions_path.read_text(encoding="utf-8")
    assert "https://self-host.example.com/mcp" in block
    assert "theseus_code_minimal_context" in block


def test_claude_code_hook_command_contains_pre_search_message(fake_config_dir: Path) -> None:
    platform = ClaudeCodePlatform()
    platform.install("https://example.com/mcp")

    import json

    settings = json.loads(platform.settings_path.read_text(encoding="utf-8"))
    commands = [
        hook["command"] for entry in settings["hooks"]["PreToolUse"] for hook in entry["hooks"]
    ]
    assert any(PRE_SEARCH_MESSAGE in cmd for cmd in commands)


def test_platform_registry_resolves_claude_code() -> None:
    assert "claude-code" in PLATFORMS
    platform = get_platform("claude-code")
    assert isinstance(platform, ClaudeCodePlatform)


def test_get_platform_unknown_raises_keyerror() -> None:
    import pytest

    with pytest.raises(KeyError):
        get_platform("does-not-exist")
