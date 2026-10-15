from __future__ import annotations

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_create_and_redirect() -> None:
    response = client.post(
        "/api/v1/urls/shorten",
        json={"original_url": "https://example.com", "alias": "demo123"},
    )
    assert response.status_code == 201
    payload = response.json()
    assert payload["alias"] == "demo123"

    redirect_response = client.get("/api/v1/urls/demo123", follow_redirects=False)
    assert redirect_response.status_code == 307
    assert redirect_response.headers["location"] == "https://example.com"
