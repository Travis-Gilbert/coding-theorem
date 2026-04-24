# coding-theorem

## Project Overview

Python CLI that installs the Theseus MCP server into local coding tools (Claude Code today; Cursor, Windsurf, Zed planned). Installed via `pip install coding-theorem`. Writes a managed block fenced by marker comments, so repeated installs replace rather than duplicate, and uninstall removes only what the installer added.

Public-facing. MIT. Deliberately neutral on any Theseus internals. Theseus is the default MCP target, not the only one: `--mcp-url` lets users point at any MCP endpoint.

## Tech Stack

Python 3.11+, click, platformdirs, rich. hatchling build backend, src/ layout. pytest + pytest-cov, ruff (format + lint), mypy strict. GitHub Actions CI (matrix: Python 3.11/3.12/3.13 x ubuntu/macos/windows). PyPI publishing via trusted publisher (OIDC, no API tokens).

## Key Directories

| Path | Purpose |
|------|---------|
| `src/coding_theorem/` | Package source: `cli.py` (click), `installer.py` (dispatcher), `config.py` (defaults + markers), `platforms/` (one file per platform) |
| `src/coding_theorem/platforms/claude_code.py` | Claude Code: writes `~/.claude/settings.json` entries (`mcpServers.theseus` + PreToolUse hook) and a managed block to `~/.claude/CLAUDE.md` |
| `tests/` | 17 tests, CliRunner + `fake_config_dir` fixture (tmp HOME) |
| `.github/workflows/ci.yml` | Lint (ruff + mypy), matrix tests, build artifact |
| `.github/workflows/publish.yml` | Tag-driven build + PyPI publish + GitHub release |

## Development Commands

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"

pytest                       # 17 tests, ~0.1s
pytest --cov                 # current floor: 85% overall

ruff format .                # apply format
ruff format --check .        # CI gate
ruff check .                 # CI gate
mypy src                     # CI gate (strict)

python -m build              # produces dist/*.tar.gz and dist/*.whl
twine check dist/*

coding-theorem --help
coding-theorem install --platform claude-code --dry-run
coding-theorem status
```

## Release Flow

1. Bump `version` in `pyproject.toml` and add a `## [x.y.z] - YYYY-MM-DD` entry to `CHANGELOG.md`.
2. Commit as `release: vX.Y.Z`.
3. `git tag vX.Y.Z && git push --tags`.
4. `publish.yml` verifies tag matches pyproject, builds, and publishes via trusted publisher to PyPI, then creates a GitHub release with dist attachments and changelog notes.

PyPI versions cannot be reused, even after yanking. Tag once per version.

## Architecture Notes

### Managed state, split by file type

Machine-readable JSON config (`~/.claude/settings.json`) uses stable keys for our entries: `mcpServers.theseus` is always our MCP server slot; the PreToolUse hook we install is detected on uninstall via the substring `coding-theorem:` in its command. Any hook entry containing that marker is treated as ours.

Human-readable markdown (`~/.claude/CLAUDE.md`) uses comment-fenced markers:

```
<!-- coding-theorem install: start -->
...assistant hints...
<!-- coding-theorem install: end -->
```

Install replaces anything between markers (or appends the block if absent). Uninstall removes the block plus a single trailing newline, preserving surrounding content.

### `--dry-run`

Every write path threads `dry_run: bool = False` through the platform methods. When `True`, each platform still computes the planned change and returns a `PlannedChange(target_path, description, diff)` but skips `write_text` / `write_json`. The CLI renderer prints the diff as-is when `dry_run` is set.

### Platform registry

`platforms.__init__.PLATFORMS` maps name to class. `get_platform(name)` raises `KeyError` with a helpful message listing available platforms. `list_platforms()` returns one instance of each registered platform. No `Platform` ABC / Protocol: concrete base class `Platform` in `platforms/base.py` raises `NotImplementedError` in abstract methods.

### Test fixture

`tests/conftest.py::fake_config_dir` sets `HOME`, `USERPROFILE` (Windows), and `XDG_CONFIG_HOME` to a `tmp_path` subdirectory. `Path.home()` in the installer resolves into the fake, so tests never touch the real user config.

## Status

| Milestone | Status |
|-----------|--------|
| Scaffold, metadata, workflows | Done |
| Claude Code platform | Done |
| Tests + lint + mypy | Done (17 tests, 85% cov) |
| Local E2E (build, twine, fresh-venv install) | Done |
| Push to GitHub (`Travis-Gilbert/coding-theorem`) | Pending, user-triggered |
| PyPI trusted publisher configured | Pending, user-triggered |
| Tag + publish v0.1.0 | Pending, user-triggered |
| Theseus private-repo doc updates | Pending, user-triggered |
| Cursor / Windsurf / Zed platforms | 0.2.0+ |

## Next Step

After `Travis-Gilbert/coding-theorem` exists on GitHub and PyPI trusted publisher is configured: `git tag v0.1.0 && git push --tags`. Then update the Theseus private repo docs to point at the public package.

## Writing Rules

- No em dashes (`---`) or en dashes (`--`) anywhere. Use colons, periods, commas, semicolons, or parentheses.
- No `Co-Authored-By` lines on commits.
- Commits as `<type>(<scope>): <description>` with required scope.
- Never expose Theseus internals in this repo's docs, code, or commit messages. The public framing is "installs an MCP server"; Theseus is the default, not the only context.
