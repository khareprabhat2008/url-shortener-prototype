from __future__ import annotations

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_orchestrator_run_creation_and_approval() -> None:
    response = client.post(
        "/api/v1/orchestrator/runs",
        json={
            "name": "demo-run",
            "nodes": [
                {"name": "lint", "type": "task"},
                {"name": "manual-gate", "type": "manual_gate", "approval_required": True},
            ],
        },
    )
    assert response.status_code == 200
    payload = response.json()
    run_id = payload["run_id"]

    response = client.post(f"/api/v1/orchestrator/runs/{run_id}/start")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "completed"

    details = client.get(f"/api/v1/orchestrator/runs/{run_id}")
    assert details.status_code == 200
    body = details.json()
    assert body["run_id"] == run_id
