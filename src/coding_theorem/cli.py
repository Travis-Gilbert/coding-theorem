"""click CLI entry point for coding-theorem."""

from __future__ import annotations

import sys

import click
from rich.console import Console
from rich.table import Table

from coding_theorem import __version__
from coding_theorem.config import MCP_URL_DEFAULT
from coding_theorem.installer import AggregateResult
from coding_theorem.installer import install as do_install
from coding_theorem.installer import status as do_status
from coding_theorem.installer import uninstall as do_uninstall

_console = Console()


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
    action = "Would install" if result.dry_run else "Installed"
    if not result.installs:
        _console.print(
            "[yellow]No platforms detected. Use --platform to target explicitly.[/yellow]"
        )
        return
    for r in result.installs:
        _console.print(
            f"[bold]{action}[/bold] on [cyan]{r.platform}[/cyan] "
            f"with MCP URL [green]{r.mcp_url}[/green]"
        )
        if not r.changes:
            _console.print("  (no changes; already configured)")
            continue
        for c in r.changes:
            _console.print(f"  - {c.description}")
            _console.print(f"    [dim]{c.target_path}[/dim]")
            if result.dry_run and c.diff:
                _console.print(c.diff, markup=False)


def _render_uninstall(result: AggregateResult) -> None:
    action = "Would remove" if result.dry_run else "Removed"
    if not result.uninstalls:
        _console.print(
            "[yellow]No platforms detected. Use --platform to target explicitly.[/yellow]"
        )
        return
    for r in result.uninstalls:
        _console.print(f"[bold]{action}[/bold] on [cyan]{r.platform}[/cyan]")
        if not r.changes:
            _console.print("  (nothing to remove)")
            continue
        for c in r.changes:
            _console.print(f"  - {c.description}")
            _console.print(f"    [dim]{c.target_path}[/dim]")


def _render_status(result: AggregateResult) -> None:
    table = Table(title="coding-theorem status")
    table.add_column("Platform")
    table.add_column("Available")
    table.add_column("Installed")
    table.add_column("MCP URL")
    for s in result.statuses:
        table.add_row(
            s.platform,
            "yes" if s.available else "no",
            "yes" if s.installed else "no",
            s.mcp_url or "",
        )
    _console.print(table)
    for s in result.statuses:
        for note in s.notes:
            _console.print(f"  [dim]{s.platform}:[/dim] {note}")


__all__ = ["main"]


if __name__ == "__main__":
    main()
