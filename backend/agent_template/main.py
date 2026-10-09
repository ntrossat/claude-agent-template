"""The web app. Holds the routes and wires the config, the agent, and the frontend together."""

import logging
from collections.abc import AsyncIterator
from pathlib import Path
from uuid import UUID

from fastapi import APIRouter, FastAPI, HTTPException
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from . import agent, config as config_module
from .config import Config

FRONTEND_DIR = Path(__file__).resolve().parents[2] / "frontend" / "dist"

log = logging.getLogger(__name__)


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=10_000)
    session_id: UUID | None = None


def sse(event: agent.ChatEvent) -> str:
    return f"data: {event.model_dump_json()}\n\n"


def create_app(config: Config | None = None) -> FastAPI:
    config = config or config_module.load()
    app = FastAPI(title="Agent template", docs_url=None, redoc_url=None, openapi_url=None)
    router = APIRouter()

    # Chat

    @router.get("/api/chat/{session_id}")
    def get_history(session_id: UUID) -> list[agent.HistoryMessage]:
        messages = agent.history(config, str(session_id))
        if not messages:
            raise HTTPException(404, "This chat no longer exists. Start a new chat.")
        return messages

    @router.post("/api/chat")
    def post_chat(request: ChatRequest) -> StreamingResponse:
        async def stream() -> AsyncIterator[str]:
            session_id = str(request.session_id) if request.session_id else None
            try:
                async for event in agent.run_turn(config, request.message, session_id):
                    yield sse(event)
            except Exception:
                log.exception("Chat turn failed")
                yield sse(agent.ErrorEvent(message="The agent couldn't answer. Check the server logs, then try again."))

        return StreamingResponse(stream(), media_type="text/event-stream", headers={"Cache-Control": "no-cache"})

    # Frontend

    if FRONTEND_DIR.is_dir():
        index = (FRONTEND_DIR / "index.html").read_text().replace("%BASE_PATH%", config.base_path)
        app.mount(f"{config.base_path}/assets", StaticFiles(directory=FRONTEND_DIR / "assets"), name="assets")

        @router.get("/", response_class=HTMLResponse)
        def get_index() -> str:
            return index

    app.include_router(router, prefix=config.base_path)
    return app
