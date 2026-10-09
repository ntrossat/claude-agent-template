# agent-template

Template for Claude agent projects, wired to [Ohara](https://ohara.trossat.com/docs) for docs and engineering guidelines.

- `.mcp.json` registers the Ohara MCP server.
- `.claude/settings.json` allows Ohara's read-only tools.
- `.claude/rules/ohara.md` tells Claude how to use the guidelines and keep docs in sync.
- `docs/` holds this project's docs, synced to Ohara (see `.ohara.yml`).
