# Development

## Requirements

| Tool | Version | For |
|---|---|---|
| Docker with Docker Compose | Any recent | `make dev` |
| Python | 3.14 | The backend |
| [uv](https://docs.astral.sh/uv/) | 0.5 or later | Backend dependencies and tests |
| Node.js | 24 | The frontend |

Docker alone is enough to run the app. Python, uv, and Node.js are for the tests and the faster split setup.

## Run it locally

```bash
cp .env.example .env   # set ANTHROPIC_API_KEY
make dev               # docker compose up --build --watch
```

Open `http://localhost:8000`. The image rebuilds on each code change.

Or run the parts separately, for faster reloads:

```bash
# Backend on port 8000
cd backend && ANTHROPIC_API_KEY=... DATA_DIR=.data uv run uvicorn agent_template.main:create_app --factory --reload

# Frontend on port 5173, proxying /api to port 8000
cd frontend && npm install && npm run dev
```

Open `http://localhost:5173`.

## Configuration

| Variable | Required | Default | What it does |
|---|---|---|---|
| `ANTHROPIC_API_KEY` | One of the two | | An API key from the Claude Console |
| `CLAUDE_CODE_OAUTH_TOKEN` | One of the two | | A Claude subscription token from `claude setup-token`. Personal use only, see below |
| `AGENT_MODEL` | No | `claude-opus-5-5` | The Claude model the agent runs on |
| `OHARA_MCP_URL` | No | | The Ohara MCP server, such as `https://ohara.example.com/docs/mcp`. Without it, the agent has no tools |
| `OHARA_TOKEN` | No | | A GitHub or `oha_` token for Ohara, such as the output of `gh auth token`. Needed only when the docs repository is private: without it, the agent runs without its tools |
| `BASE_PATH` | No | | The path the app is served under, such as `/agent` |
| `DATA_DIR` | No | `/data` | Where sessions are kept |

Anthropic doesn't allow products that other people use to run on a claude.ai login or subscription limits. Use `CLAUDE_CODE_OAUTH_TOKEN` only for an instance that you alone use. Anything else needs `ANTHROPIC_API_KEY`.

## Test

```bash
make test   # backend tests, then the frontend type check and build
```

Or one part at a time:

```bash
cd backend && uv run pytest
cd frontend && npm run build
```

Backend tests replace the SDK's `query()` and `get_session_messages()` with fakes, so they need no network and no key. Each test gets its own data directory. `tests/conftest.py` provides:

| Fixture | Gives |
|---|---|
| `env` (autouse) | A temporary data directory and a fake API key |
| `config` | The loaded configuration |
| `client` | A test client for the app |

Add tests next to the area they cover: `test_chat.py` for the routes, `test_agent.py` for the configuration and the agent options.

## Project layout

```text
backend/agent_template/   FastAPI app, see Architecture
backend/tests/            pytest tests
frontend/src/             React app
docs/                     these docs, synced into Ohara by .ohara.yml
.github/workflows/        CI
Dockerfile                builds the frontend, then the backend image
docker-compose.yml        one service and the data volume
```

## Deploy

The image runs anywhere Docker does. It runs as a non-root user and keeps its state in the `/data` volume. Set the variables above in the environment. The app has no sign-in, so put it behind your own access control before exposing it beyond your machine.

## Conventions

- Work on a branch, never on `main`, and merge through a pull request.
- Use [Conventional Commits](https://www.conventionalcommits.org): `feat:`, `fix:`, `docs:`, `ci:`, `chore:`.
- Update these docs in the same pull request as the code they describe.
