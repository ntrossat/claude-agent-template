import pytest

from agent_template import agent, config as config_module


def test_config_requires_credentials(monkeypatch):
    monkeypatch.delenv("ANTHROPIC_API_KEY")
    with pytest.raises(config_module.ConfigError):
        config_module.load()


def test_config_accepts_subscription_token(monkeypatch):
    monkeypatch.delenv("ANTHROPIC_API_KEY")
    monkeypatch.setenv("CLAUDE_CODE_OAUTH_TOKEN", "test-token")
    assert config_module.load().model == config_module.DEFAULT_MODEL


def test_config_keeps_sessions_on_the_data_volume(tmp_path):
    import os

    config = config_module.load()
    assert os.environ["CLAUDE_CONFIG_DIR"] == str(tmp_path / "claude")
    assert config.workspace.is_dir()


def test_config_clears_the_mcp_needs_auth_cache_on_start(tmp_path):
    cache = tmp_path / "claude" / config_module.NEEDS_AUTH_CACHE
    cache.parent.mkdir(parents=True)
    cache.write_text('{"ohara": {"timestamp": 1}}')
    config_module.load()
    assert not cache.exists()


def test_options_without_ohara_have_no_tools(config):
    options = agent.options(config, None)
    assert options.tools == []
    assert options.mcp_servers == {}
    assert options.allowed_tools == []


def test_options_with_ohara_allow_only_read_tools(monkeypatch):
    monkeypatch.setenv("OHARA_MCP_URL", "https://docs.example.com/mcp")
    options = agent.options(config_module.load(), "4f1c2b8e-0000-4000-8000-000000000000")
    assert options.mcp_servers == {"ohara": {"type": "http", "url": "https://docs.example.com/mcp"}}
    assert options.allowed_tools == ["mcp__ohara__list_pages", "mcp__ohara__search", "mcp__ohara__read_page", "mcp__ohara__stale_pages"]
    assert "mcp__ohara__propose_change" in options.disallowed_tools
    assert options.resume == "4f1c2b8e-0000-4000-8000-000000000000"


def test_options_send_the_ohara_token_when_set(monkeypatch):
    monkeypatch.setenv("OHARA_MCP_URL", "https://docs.example.com/mcp")
    monkeypatch.setenv("OHARA_TOKEN", "oha_test")
    server = agent.options(config_module.load(), None).mcp_servers["ohara"]
    assert server["headers"] == {"Authorization": "Bearer oha_test"}
