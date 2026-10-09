# Build the frontend.
FROM node:24-slim AS frontend
WORKDIR /app/frontend
COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci
COPY frontend/ ./
RUN npm run build

# Run the backend, which serves the built frontend.
FROM python:3.14-slim
COPY --from=ghcr.io/astral-sh/uv:0.5.4 /uv /bin/uv
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy UV_PROJECT_ENVIRONMENT=/app/.venv PATH="/app/.venv/bin:$PATH" DATA_DIR=/data
WORKDIR /app/backend
COPY backend/pyproject.toml backend/uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project
COPY backend/ ./
RUN uv sync --frozen --no-dev
COPY --from=frontend /app/frontend/dist /app/frontend/dist

RUN useradd --create-home --uid 1000 agent && mkdir -p /data && chown agent:agent /data
USER agent
VOLUME /data
EXPOSE 8000
CMD ["uvicorn", "agent_template.main:create_app", "--factory", "--host", "0.0.0.0", "--port", "8000"]
