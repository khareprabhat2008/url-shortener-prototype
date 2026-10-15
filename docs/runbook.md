# Runbook

## Health checks

- API health: `GET /health`
- Orchestrator health: `GET /health`

## Common operations

### Create a short URL

```bash
curl -X POST http://localhost:8000/api/v1/urls/shorten \
  -H 'Content-Type: application/json' \
  -d '{"original_url":"https://example.com","alias":"example"}'
```

### Redirect

```bash
curl -I http://localhost:8000/api/v1/urls/example
```

### Inspect analytics

```bash
curl http://localhost:8000/api/v1/urls/example/stats
curl http://localhost:8000/api/v1/analytics/summary
```

## Human approval flow for orchestrator

1. Create an orchestration run.
2. Start it.
3. A node marked `manual_gate` pauses execution.
4. Approve it through `POST /api/v1/orchestrator/runs/{run_id}/approve/{node_id}`.
5. The workflow continues until success or rollback.

## Rollback and restart

This prototype exposes workflow state so a human may re-run or stop a given orchestration run. In production, this would be backed by stronger deployment and database snapshot policies.
