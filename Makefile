.PHONY: dev test

dev:
	docker compose up --build --watch

test:
	cd backend && uv run pytest
	cd frontend && npm run build
