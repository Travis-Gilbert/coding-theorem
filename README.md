# coding-theorem

Installs the [Theseus](https://github.com/Travis-Gilbert/theseus) MCP server into your local coding tools, so your editor can query a knowledge graph of your codebase instead of grepping raw files every time.

Today this means Claude Code. Cursor, Windsurf, and Zed are on the roadmap.

## Why

Most coding assistants search text. When you ask about a function, they grep. When you ask how two systems connect, they grep twice and guess. This works until the codebase is big enough that grep returns either nothing useful or too much to read.

Theseus builds and maintains a structured graph of your code, docs, and design decisions. The graph knows which functions call which, where a concept was defined, which commits changed a module and why, and which claims are contested. An MCP server exposes this graph as tools your editor can call directly.

`coding-theorem` is the thing that wires your editor up to that server. No manual config file editing, no copying UUIDs between windows.

## Install

```bash
pip install coding-theorem
coding-theorem install
```

That installs for every detected platform. Target one explicitly:

```bash
coding-theorem install --platform claude-code
```

Use a self-hosted Theseus instance instead of the default:

```bash
coding-theorem --mcp-url http://localhost:8001/mcp install --platform claude-code
```

Restart your editor. The Theseus server should appear in the tool list.

## Verify

```bash
coding-theorem status
```

Shows which platforms are configured, which are available to configure, and which MCP URL each one points at.

For Claude Code specifically, a quick manual check:

1. Restart Claude Code in a repository that Theseus has indexed.
2. Run a Grep or Glob.
3. Confirm the hook output includes: `coding-theorem: use theseus_code_minimal_context(task) before searching raw files`.

If that line appears, the hook is firing and the MCP connection is live.

## Uninstall

```bash
coding-theorem uninstall
```

This removes only the managed block and the hook files that `coding-theorem` created. Your existing config is preserved.

## How it works

The installer writes a managed block to each platform's config directory, fenced by markers:

```
<!-- coding-theorem install: start -->
...generated config...
<!-- coding-theorem install: end -->
```

Running `install` twice replaces the block instead of duplicating it. Running `uninstall` removes only what's inside the markers. Anything you added yourself outside the fences is untouched.

Specifically, `coding-theorem install --platform claude-code` will:
- Add a Theseus entry to Claude Code's MCP server list
- Install a pre-search hook that reminds the model to use graph tools before grep
- Write assistant hints that describe the available Theseus tools

Run with `--dry-run` to see exactly what would change without writing anything.

## Supported platforms

| Platform | Status |
|----|----|
| Claude Code | Supported |
| Cursor | Planned |
| Windsurf | Planned |
| Zed | Planned |

If you want to add a platform, the pattern is in `src/coding_theorem/platforms/claude_code.py`. Open an issue first so we can agree on the config shape before you start.

## Requirements

- Python 3.11+
- A reachable Theseus MCP endpoint (hosted default or self-hosted)
- One of the supported editors

## Hosted vs. self-hosted

The default MCP URL points at the hosted Theseus endpoint. That's fine for trying the tool out, and fine for public repositories.

For private code, self-host. Theseus is open source. Point `--mcp-url` at your instance and your graph data never leaves your network.

## License

MIT. See [LICENSE](LICENSE).

## Related

- [Theseus](https://github.com/Travis-Gilbert/theseus): the knowledge graph engine that powers the MCP server
- [Model Context Protocol](https://modelcontextprotocol.io): the spec this builds on
