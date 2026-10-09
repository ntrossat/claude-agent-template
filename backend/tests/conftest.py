import pytest
from fastapi.testclient import TestClient

from agent_template import config as config_module
from agent_template.main import create_app


@pytest.fixture(autouse=True)
def env(tmp_path, monkeypatch):
    """Each test gets its own data directory and a fake API key."""
    for name in ["CLAUDE_CODE_OAUTH_TOKEN", "OHARA_MCP_URL", "OHARA_TOKEN", "AGENT_MODEL", "BASE_PATH"]:
        monkeypatch.delenv(name, raising=False)
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
    monkeypatch.setenv("DATA_DIR", str(tmp_path))
    monkeypatch.setenv("CLAUDE_CONFIG_DIR", str(tmp_path / "claude"))


@pytest.fixture
def config():
    return config_module.load()


@pytest.fixture
def client(config):
    return TestClient(create_app(config))
