"""Configuration. The only module that reads the environment."""

import os
from dataclasses import dataclass
from pathlib import Path

DEFAULT_MODEL = "claude-opus-5-5"
NEEDS_AUTH_CACHE = "mcp-needs-auth-cache.json"


class ConfigError(Exception):
    """A required setting is missing."""


@dataclass(frozen=True)
class Config:
    model: str
    data_dir: Path
    base_path: str
    ohara_mcp_url: str | None
    ohara_token: str | None

    @property
    def claude_dir(self) -> Path:
        return self.data_dir / "claude"

    @property
    def workspace(self) -> Path:
        return self.data_dir / "workspace"


def load() -> Config:
    """Read the settings and prepare the data directory.

    The Agent SDK reads ANTHROPIC_API_KEY or CLAUDE_CODE_OAUTH_TOKEN from the environment itself,
    so they are only checked here, never copied or logged.
    """
    if not (os.environ.get("ANTHROPIC_API_KEY") or os.environ.get("CLAUDE_CODE_OAUTH_TOKEN")):
        raise ConfigError("Set ANTHROPIC_API_KEY (or CLAUDE_CODE_OAUTH_TOKEN for personal use) in .env, then restart.")

    config = Config(
        model=os.environ.get("AGENT_MODEL") or DEFAULT_MODEL,
        data_dir=Path(os.environ.get("DATA_DIR") or "/data"),
        base_path=(os.environ.get("BASE_PATH") or "").rstrip("/"),
        ohara_mcp_url=os.environ.get("OHARA_MCP_URL") or None,
        ohara_token=os.environ.get("OHARA_TOKEN") or None,
    )
    config.claude_dir.mkdir(parents=True, exist_ok=True)
    config.workspace.mkdir(parents=True, exist_ok=True)
    # Keeps the SDK's session transcripts on the data volume, so a restart resumes them.
    os.environ["CLAUDE_CONFIG_DIR"] = str(config.claude_dir)
    # The CLI skips an MCP server that once answered 401 until this cache expires. Clearing it on start
    # lets a new OHARA_TOKEN work right after a restart.
    (config.claude_dir / NEEDS_AUTH_CACHE).unlink(missing_ok=True)
    return config
