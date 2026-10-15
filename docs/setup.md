# Setup Instructions

## Prerequisites

- Docker Desktop or Docker Engine
- Docker Compose v2
- Python 3.11 (if you want to run locally without Docker)

## Local startup

```bash
cp .env.example .env

docker compose up --build
```

This starts:
- PostgreSQL on localhost:5432
- Redis on localhost:6379
- API on localhost:8000
- Orchestrator on localhost:9000

## OpenAPI docs

- API docs: http://localhost:8000/docs
- Orchestrator docs: http://localhost:9000/docs

## Smoke test

```bash
python scripts/smoke_test.py
```

## Local Python fallback

If you want to run only the API service without Docker:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
export DATABASE_URL=sqlite+aiosqlite:///./shortener.db
export REDIS_URL=redis://localhost:6379/0
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```
