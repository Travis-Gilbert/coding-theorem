"""Tests for the click CLI wrapper."""

from __future__ import annotations

from pathlib import Path

from click.testing import CliRunner

from coding_theorem.cli import main


def test_install_command_exits_zero(fake_config_dir: Path) -> None:
    runner = CliRunner()
    result = runner.invoke(main, ["install", "--platform", "claude-code"])
    assert result.exit_code == 0, result.output
    assert (fake_config_dir / ".claude" / "CLAUDE.md").exists()


def test_install_unknown_platform_exits_nonzero(fake_config_dir: Path) -> None:
    runner = CliRunner()
    result = runner.invoke(main, ["install", "--platform", "does-not-exist"])
    assert result.exit_code != 0
    assert "does-not-exist" in result.output


def test_custom_mcp_url_flows_into_generated_block(fake_config_dir: Path) -> None:
    runner = CliRunner()
    result = runner.invoke(
        main,
        ["--mcp-url", "https://self.example.com/mcp", "install", "--platform", "claude-code"],
    )
    assert result.exit_code == 0, result.output
    block = (fake_config_dir / ".claude" / "CLAUDE.md").read_text(encoding="utf-8")
    assert "https://self.example.com/mcp" in block


def test_status_command_runs(fake_config_dir: Path) -> None:
    runner = CliRunner()
    result = runner.invoke(main, ["status"])
    assert result.exit_code == 0, result.output
    assert "claude-code" in result.output


def test_dry_run_command_writes_nothing(fake_config_dir: Path) -> None:
    (fake_config_dir / ".claude").mkdir(parents=True, exist_ok=True)
    runner = CliRunner()
    result = runner.invoke(main, ["install", "--platform", "claude-code", "--dry-run"])
    assert result.exit_code == 0, result.output
    assert not (fake_config_dir / ".claude" / "CLAUDE.md").exists()
    assert not (fake_config_dir / ".claude" / "settings.json").exists()
