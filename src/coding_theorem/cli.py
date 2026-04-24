"""click CLI entry point for coding-theorem."""

from __future__ import annotations

import sys
from pathlib import Path

import click
from rich.console import Console
from rich.padding import Padding
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from coding_theorem import __version__
from coding_theorem.config import MCP_URL_DEFAULT, PRE_SEARCH_MESSAGE
from coding_theorem.installer import AggregateResult
from coding_theorem.installer import install as do_install
from coding_theorem.installer import status as do_status
from coding_theorem.installer import uninstall as do_uninstall

_console = Console()

# Theseus brand palette, matched to travisgilbert.me section colors.
_TEAL = "#2D5F6B"
_GOLD = "#C49A4A"
_TERRACOTTA = "#B45A2D"


def _wordmark(suffix: str = "") -> Text:
    """`Theseus · coding-theorem 0.1.1[ · <suffix>]` as a rich Text."""
    t = Text("  ")
    t.append("Theseus", style=f"bold {_TEAL}")
    t.append(" · ", style="dim")
    t.append("coding-theorem", style="bold")
    t.append(f" {__version__}", style="dim")
    if suffix:
        t.append(" · ", style="dim")
        t.append(suffix, style="dim")
    return t


def _tildify(path: str) -> str:
    """Replace a leading $HOME with `~` for display."""
    home = str(Path.home())
    if path.startswith(home):
        return "~" + path[len(home) :]
    return path


def _tag(label: str, color: str) -> Text:
    t = Text("  ")
    t.append(f"[{label}]", style=f"bold {color}")
    t.append(" ")
    return t


def _next_panel() -> Padding:
    body = Text()
    body.append("restart Claude Code to connect.\n")
    body.append("verify anytime:  ")
    body.append("coding-theorem status", style=f"bold {_TEAL}")
    panel = Panel(body, title="next", border_style=_TEAL, padding=(1, 2), width=72)
    return Padding(panel, (0, 0, 0, 2))


def _render_reminder_preview() -> None:
    """Print the exact string the user will see in Claude Code after restart."""
    header = Text("your first Grep or Glob will print:", style="dim")
    reminder = Text(PRE_SEARCH_MESSAGE, style=_TEAL)
    _console.print(Padding(header, (0, 0, 0, 2)))
    _console.print(Padding(reminder, (0, 0, 0, 4)))


@click.group()
@click.version_option(__version__, package_name="coding-theorem")
@click.option(
    "--mcp-url",
    default=MCP_URL_DEFAULT,
    show_default=True,
    envvar="CODING_THEOREM_MCP_URL",
    help="Theseus MCP server URL. Pass to target a self-hosted instance.",
)
@click.pass_context
def main(ctx: click.Context, mcp_url: str) -> None:
    """Install the Theseus MCP server into local coding tools."""
    ctx.ensure_object(dict)
    ctx.obj["mcp_url"] = mcp_url


@main.command("install")
@click.option(
    "--platform",
    "platform",
    default=None,
    help="Target a specific platform. Default: every detected platform.",
)
@click.option(
    "--dry-run",
    is_flag=True,
    default=False,
    help="Report changes without writing files.",
)
@click.pass_context
def install_cmd(ctx: click.Context, platform: str | None, dry_run: bool) -> None:
    """Install the Theseus MCP server."""
    try:
        result = do_install(platform=platform, mcp_url=ctx.obj["mcp_url"], dry_run=dry_run)
    except KeyError as e:
        _console.print(f"[red]error:[/red] {e}")
        sys.exit(2)
    _render_install(result)


@main.command("uninstall")
@click.option(
    "--platform",
    "platform",
    default=None,
    help="Target a specific platform. Default: every detected platform.",
)
@click.option(
    "--dry-run",
    is_flag=True,
    default=False,
    help="Report changes without writing files.",
)
def uninstall_cmd(platform: str | None, dry_run: bool) -> None:
    """Remove the Theseus MCP server entries this installer created."""
    try:
        result = do_uninstall(platform=platform, dry_run=dry_run)
    except KeyError as e:
        _console.print(f"[red]error:[/red] {e}")
        sys.exit(2)
    _render_uninstall(result)


@main.command("status")
@click.option(
    "--platform",
    "platform",
    default=None,
    help="Target a specific platform. Default: every registered platform.",
)
def status_cmd(platform: str | None) -> None:
    """Report which platforms are configured."""
    try:
        result = do_status(platform=platform)
    except KeyError as e:
        _console.print(f"[red]error:[/red] {e}")
        sys.exit(2)
    _render_status(result)


def _render_install(result: AggregateResult) -> None:
    _console.print()
    _console.print(_wordmark("dry-run" if result.dry_run else ""))
    _console.print()

    if not result.installs:
        _console.print(_tag("--", "dim"))
        _console.print(f"  [{_TERRACOTTA}]no platforms detected. pass --platform to target.[/]")
        _console.print()
        return

    tag_label = "plan" if result.dry_run else "ok"
    tag_color = _TEAL if result.dry_run else _GOLD
    any_changes = False

    for r in result.installs:
        if not r.changes:
            line = _tag("--", "dim")
            line.append(f"already configured on {r.platform}", style="dim")
            _console.print(line)
            _console.print(f"       [dim]MCP URL: {r.mcp_url}[/dim]")
            continue
        any_changes = True
        for c in r.changes:
            line = _tag(tag_label, tag_color)
            line.append(c.description)
            _console.print(line)
            _console.print(f"       [dim]{_tildify(c.target_path)}[/dim]")

    _console.print()

    if result.dry_run:
        _console.print("  [dim](nothing written. re-run without --dry-run to apply.)[/dim]")
        _console.print()
        return

    if any_changes:
        _console.print(_next_panel())
        _console.print()
        _render_reminder_preview()
        _console.print()
        _console.print("  [dim](no server probe performed. restart Claude Code to verify.)[/dim]")
        _console.print()


def _render_uninstall(result: AggregateResult) -> None:
    _console.print()
    _console.print(_wordmark("dry-run" if result.dry_run else ""))
    _console.print()

    if not result.uninstalls:
        _console.print(f"  [{_TERRACOTTA}]no platforms detected. pass --platform to target.[/]")
        _console.print()
        return

    tag_label = "plan" if result.dry_run else "ok"
    tag_color = _TEAL if result.dry_run else _GOLD

    for r in result.uninstalls:
        if not r.changes:
            line = _tag("--", "dim")
            line.append(f"nothing to remove on {r.platform}", style="dim")
            _console.print(line)
            continue
        for c in r.changes:
            line = _tag(tag_label, tag_color)
            line.append(c.description)
            _console.print(line)
            _console.print(f"       [dim]{_tildify(c.target_path)}[/dim]")

    _console.print()
    if result.dry_run:
        _console.print("  [dim](nothing written. re-run without --dry-run to apply.)[/dim]")
    else:
        _console.print("  [dim](anything outside the managed markers is untouched.)[/dim]")
    _console.print()


def _render_status(result: AggregateResult) -> None:
    _console.print()
    _console.print(_wordmark())
    _console.print()

    table = Table(
        show_header=True,
        header_style=f"bold {_TEAL}",
        border_style="dim",
        padding=(0, 1),
    )
    table.add_column("platform")
    table.add_column("available")
    table.add_column("installed")
    table.add_column("MCP URL", overflow="fold")

    for s in result.statuses:
        available_txt = f"[{_GOLD}]yes[/]" if s.available else "[dim]no[/dim]"
        installed_txt = f"[{_GOLD}]yes[/]" if s.installed else "[dim]no[/dim]"
        mcp_url_txt = s.mcp_url or "[dim]-[/dim]"
        table.add_row(s.platform, available_txt, installed_txt, mcp_url_txt)
    _console.print(Padding(table, (0, 0, 0, 2)))

    _console.print()
    for s in result.statuses:
        for note in s.notes:
            _console.print(f"  [dim]{s.platform}:[/dim] {note}")
    _console.print()


__all__ = ["main"]


if __name__ == "__main__":
    main()
