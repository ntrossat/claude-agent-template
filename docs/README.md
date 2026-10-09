# Claude agent template

A starting point for agents built on the Claude Agent SDK. It ships a chat in the browser that talks to a FastAPI backend, which runs the agent through the SDK. The agent reads your team's docs through the Ohara MCP server.

| Page | Covers |
|---|---|
| [Architecture](architecture.md) | Components, how a chat turn flows, where state lives, and how to add a tool |
| [Development](development.md) | Run it locally, configure it, test it, and deploy it |

## Stack

| Part | Technology |
|---|---|
| Backend | Python 3.14, FastAPI, Pydantic, Claude Agent SDK, managed with `uv` |
| Frontend | React with TypeScript, built with Vite. Replies render as Markdown with react-markdown and remark-gfm |
| Packaging | One Docker image: the frontend is built, then served by FastAPI |
| CI | GitHub Actions: backend tests and frontend build on each pull request and push to `main` |

## Working with Ohara

| File | What it does |
|---|---|
| `.mcp.json` | Registers the Ohara MCP server for everyone who opens the project in Claude Code |
| `.claude/settings.json` | Allows Ohara's read-only tools. Proposing a docs change still asks for confirmation |
| `.claude/rules/ohara.md` | Tells Claude which guidelines apply and how to keep the docs in sync |
| `.ohara.yml` | Lists the folders Ohara syncs. Here, `docs/` |

1. Pages in `docs/` describe this project. Edit them in the same change as the code.
2. When a push reaches `main`, Ohara syncs `docs/` into `apps/claude-agent-template/`.
3. Every other page, including the guidelines, lives in Ohara. Claude proposes changes to it as a pull request, and a person approves them.
