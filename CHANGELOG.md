# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.1] - 2026-04-24

### Changed

- Reworked CLI output for `install`, `uninstall`, and `status`. Theseus wordmark at top, gold `[ok]` / teal `[plan]` change markers, paths shown with a leading `~` where possible, a bordered "next" panel summarising the restart-and-verify flow after install.
- Added an explicit `(no server probe performed. restart Claude Code to verify.)` note after install, to make the installer's narrow scope visible (it writes config and nothing more).

### Notes

- No changes to the managed block content, markers, MCP server entry, or hook command. Upgrading from 0.1.0 does not require re-running `install`.

## [0.1.0] - 2026-04-24

### Added

- Initial public release.
- `coding-theorem install` / `uninstall` / `status` commands.
- `--platform claude-code` support for Claude Code.
- `--mcp-url` flag to target self-hosted Theseus instances.
- `--dry-run` flag that reports changes without writing files.
- Managed-block markers so repeated installs replace rather than duplicate.
- Pre-search hook reminding the model to use graph tools before grep.

[Unreleased]: https://github.com/Travis-Gilbert/coding-theorem/compare/v0.1.1...HEAD
[0.1.1]: https://github.com/Travis-Gilbert/coding-theorem/releases/tag/v0.1.1
[0.1.0]: https://github.com/Travis-Gilbert/coding-theorem/releases/tag/v0.1.0
