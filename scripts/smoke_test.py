from __future__ import annotations

from fastapi import FastAPI, HTTPException

app = FastAPI(title="orchestrator", version="0.1.0")


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/api/v1/orchestrator/overview")
async def overview() -> dict[str, str]:
    return {
        "status": "operational",
        "model": "dag-with-approval-gates",
        "notes": "This prototype demonstrates the governance model and not a full enterprise scheduler.",
    }
