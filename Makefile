.PHONY: install dev test lint api dashboard frontend docker-up docker-down docker-build help

# ── local setup ──────────────────────────────────────────────────────────────
install:
	pip install -r requirements-dev.txt

# ── run ──────────────────────────────────────────────────────────────────────
api:
	uvicorn app.main:app --reload --host 127.0.0.1 --port 8000

dashboard:
	streamlit run dashboard.py

frontend:
	python -m http.server 5173 --directory frontend

dev: ## Start API and dashboard side by side (requires two terminals; use docker-up instead)
	$(MAKE) api & $(MAKE) dashboard

# ── quality ──────────────────────────────────────────────────────────────────
test:
	pytest tests/ -v

lint:
	python -m py_compile app/main.py
	python -m compileall -q app dashboard.py

# ── docker ───────────────────────────────────────────────────────────────────
docker-build:
	docker build -t agentic-client-guardian:latest .

docker-up:
	docker compose up --build

docker-down:
	docker compose down

# ── help ─────────────────────────────────────────────────────────────────────
help:
	@echo "Available commands:"
	@echo "  make install       Install all dev dependencies"
	@echo "  make api           Run FastAPI with hot-reload"
	@echo "  make frontend      Serve HTML frontend on http://localhost:5173"
	@echo "  make dashboard     Run Streamlit dashboard"
	@echo "  make test          Run test suite"
	@echo "  make lint          Compile-check all Python sources"
	@echo "  make docker-build  Build Docker image"
	@echo "  make docker-up     Start API + dashboard via docker compose"
	@echo "  make docker-down   Stop docker compose services"
