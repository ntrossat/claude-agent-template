import json

from claude_agent_sdk import AssistantMessage, ResultMessage, SessionMessage, StreamEvent, ToolUseBlock

from agent_template import agent

SESSION = "4f1c2b8e-0000-4000-8000-000000000000"


def result(is_error=False, text=None):
    return ResultMessage(
        subtype="success", duration_ms=1, duration_api_ms=1, is_error=is_error, num_turns=1, session_id=SESSION, result=text
    )


def delta(text):
    event = {"type": "content_block_delta", "index": 0, "delta": {"type": "text_delta", "text": text}}
    return StreamEvent(uuid="u", session_id=SESSION, event=event)


def fake_query(*items):
    async def query(prompt, options):
        for item in items:
            yield item

    return query


def events(response):
    return [json.loads(line.removeprefix("data: ")) for line in response.text.split("\n\n") if line]


def test_chat_streams_text_then_done(client, monkeypatch):
    monkeypatch.setattr(agent, "query", fake_query(delta("Hel"), delta("lo"), result()))
    response = client.post("/api/chat", json={"message": "Hi"})
    assert response.headers["content-type"].startswith("text/event-stream")
    assert events(response) == [
        {"type": "text", "delta": "Hel"},
        {"type": "text", "delta": "lo"},
        {"type": "done", "session_id": SESSION},
    ]


def test_chat_reports_tool_calls(client, monkeypatch):
    call = AssistantMessage(content=[ToolUseBlock(id="t", name="mcp__ohara__search", input={"query": "backend"})], model="m")
    monkeypatch.setattr(agent, "query", fake_query(call, result()))
    assert events(client.post("/api/chat", json={"message": "Hi"}))[0] == {"type": "tool", "name": "search", "input": {"query": "backend"}}


def test_chat_resumes_the_given_session(client, monkeypatch):
    seen = {}

    async def query(prompt, options):
        seen["resume"] = options.resume
        yield result()

    monkeypatch.setattr(agent, "query", query)
    client.post("/api/chat", json={"message": "Hi", "session_id": SESSION})
    assert seen["resume"] == SESSION


def test_chat_reports_an_agent_error_once_with_its_reason(client, monkeypatch):
    async def query(prompt, options):
        yield result(is_error=True, text="Invalid API key")
        raise RuntimeError("raised by the SDK after an error result")

    monkeypatch.setattr(agent, "query", query)
    assert events(client.post("/api/chat", json={"message": "Hi"})) == [
        {"type": "error", "message": "Invalid API key. Send your message again once it is fixed."}
    ]


def test_chat_turns_an_exception_into_a_readable_error(client, monkeypatch):
    async def query(prompt, options):
        raise RuntimeError("secret detail")
        yield

    monkeypatch.setattr(agent, "query", query)
    last = events(client.post("/api/chat", json={"message": "Hi"}))[-1]
    assert last["type"] == "error"
    assert "secret detail" not in last["message"]


def test_chat_rejects_an_invalid_session_id(client):
    assert client.post("/api/chat", json={"message": "Hi", "session_id": "../etc"}).status_code == 422


def test_chat_rejects_an_empty_message(client):
    assert client.post("/api/chat", json={"message": ""}).status_code == 422


def test_history_of_an_unknown_session_is_not_found(client):
    assert client.get(f"/api/chat/{SESSION}").status_code == 404


def test_history_returns_the_text_of_each_message(client, monkeypatch):
    messages = [
        SessionMessage(type="user", uuid="1", session_id=SESSION, message={"role": "user", "content": "Hi"}),
        SessionMessage(
            type="assistant",
            uuid="2",
            session_id=SESSION,
            message={"role": "assistant", "content": [{"type": "tool_use", "id": "t", "name": "x", "input": {}}, {"type": "text", "text": "Hello"}]},
        ),
        SessionMessage(type="user", uuid="3", session_id=SESSION, message={"role": "user", "content": [{"type": "tool_result", "tool_use_id": "t"}]}),
    ]
    monkeypatch.setattr(agent, "get_session_messages", lambda session_id, directory: messages)
    assert client.get(f"/api/chat/{SESSION}").json() == [{"role": "user", "text": "Hi"}, {"role": "assistant", "text": "Hello"}]
