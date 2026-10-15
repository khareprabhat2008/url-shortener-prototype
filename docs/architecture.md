# Architecture Overview

The solution is built around a small but realistic set of services:

## Components

### API service
A FastAPI application owns the public contract for URL creation and redirects. It validates requests, persists URLs, and produces audit-friendly events.

### Persistence layer
PostgreSQL stores durable records for:
- URLs created by the shortener
- Click events and aggregated metrics
- Workflow runs and orchestration state

### Event queue
Redis handles asynchronous click ingest so redirect operations are fast and analytics can be processed separately without blocking user requests.

### Analytics worker
A Python worker consumes Redis click events and writes durable records to the database. This decouples redirect traffic from analytics generation.

### Orchestrator
A governance layer executes SDLC-style DAG actions with gates, retries, and human approval nodes. It is intentionally conservative: approvals are required for deploy-like actions, and state is retained for auditable traceability.

## Control flow

1. The user submits a create-short-url request.
2. API validates URL and alias constraints.
3. Postgres stores the canonical mapping.
4. The redirect endpoint resolves the alias and enqueues a click event asynchronously.
5. The worker ingests click events and writes them to analytics tables.
6. The orchestrator manages multi-stage execution using explicit dependencies and approval checkpoints.

## Engineering principles

- Modularity: separate API, worker, and orchestration concerns
- Reliability: DB durability, background analytics, retry-ready execution
- Controlled autonomy: humans approve high-impact workflow steps
- Traceability: orchestration state and events are auditable
- Minimal but real: this is a working prototype suitable for iteration and extension
