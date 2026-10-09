# Ohara instructions

Ohara at https://ohara.trossat.com/docs is the source of truth for documentation and engineering guidelines.

## Docs

- This project's docs live in this repository, in `docs/` (listed in `.ohara.yml`). Ohara syncs them into `apps/claude-agent-template/`. Update them in the same change as the code.
- Every other page lives in Ohara. Propose changes to it, never add it to this repository.

## Guidelines

| Page | What it covers |
|---|---|
| `guidelines/principles` | What we build and how we decide: simple by design, open source, config and `.env.example` |
| `guidelines/backend` | Python 3.14, FastAPI and `uv`: structure, style, state, errors, external APIs |
| `guidelines/frontend` | React and TypeScript |
| `guidelines/security` | Access, tokens, secrets, and untrusted content |
| `guidelines/testing` | What to test and how |
| `guidelines/git` | Branches, commits, pull requests, CI and CD |
| `guidelines/writing-docs` | Where docs live, their format, and their voice |
| `design/brand`, `design/style-guide`, `design/ui-kit` | Brand, style guide, and UI kit for anything user-facing |

## Project docs

| Page | What it covers |
|---|---|
| `docs/README.md` (`apps/claude-agent-template`) | Overview: what the template is, the stack, and how docs sync with Ohara |
| `docs/architecture.md` (`apps/claude-agent-template/architecture`) | Components, a chat turn and its events, routes, state, tools, and access |
| `docs/development.md` (`apps/claude-agent-template/development`) | Run locally, configuration, tests, layout, deploy, and conventions |

## Workflow

1. Before planning a change, read the guidelines and docs that apply, and search Ohara for anything else relevant. Say when a page you rely on is stale.
2. Propose an architecture that follows the guidelines, and name the guidelines it relies on.
3. After the change, check it against the guidelines and fix what does not follow them.
4. Then update this project's docs in `docs/` in the same change, and propose updates to every other page the change affects in one `propose_change`, with the project `claude-agent-template` and the active git branch, so each code branch gets a single pull request to review. Put the docs pull request links in the code pull request's description.
