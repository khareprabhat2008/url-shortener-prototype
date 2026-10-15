from __future__ import annotations

import uuid
from datetime import datetime, timedelta
from typing import Any

from fastapi import FastAPI, HTTPException, Query, status
from fastapi.responses import RedirectResponse
from pydantic import BaseModel, Field, HttpUrl, field_validator

from app.core.config import settings
from app.db.session import init_db, get_db_session
from app.models.click_event import ClickEvent
from app.models.orchestration import OrchestrationNode, OrchestrationRun
from app.models.short_url import ShortUrl
from app.services.redis_manager import redis_client
from app.services.shortener import UrlShortenerService

app = FastAPI(title=settings.app_name, version="0.1.0")


class CreateShortUrlRequest(BaseModel):
    original_url: str = Field(..., description="Full original URL")
    alias: str | None = Field(default=None, min_length=3, max_length=32)
    expires_at: datetime | None = None

    @field_validator("original_url")
    @classmethod
    def valid_url(cls, value: str) -> str:
        try:
            import urllib.parse
            parsed = urllib.parse.urlparse(value)
            if not parsed.scheme or not parsed.netloc:
                raise ValueError("URL must include scheme and host")
        except Exception as exc:
            raise ValueError("Invalid URL format") from exc
        return value

    @field_validator("alias")
    @classmethod
    def normalize_alias(cls, value: str | None) -> str | None:
        if value is None:
            return None
        return value.strip().lower()


class ShortUrlResponse(BaseModel):
    id: str
    short_url: str
    original_url: str
    alias: str
    created_at: datetime
    expires_at: datetime | None


class AnalyticsSummary(BaseModel):
    total_urls: int
    active_urls: int
    total_clicks: int
    last_24h_clicks: int


@app.on_event("startup")
async def startup() -> None:
    await init_db()


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/api/v1/urls/shorten", response_model=ShortUrlResponse, status_code=status.HTTP_201_CREATED)
async def create_short_url(payload: CreateShortUrlRequest) -> ShortUrlResponse:
    async with get_db_session() as session:
        service = UrlShortenerService(session)
        result = await service.create_short_url(
            original_url=payload.original_url,
            alias=payload.alias,
            expires_at=payload.expires_at,
        )
        return ShortUrlResponse(
            id=str(result.id),
            short_url=f"{settings.public_base_url.rstrip('/')}/{result.alias}",
            original_url=result.original_url,
            alias=result.alias,
            created_at=result.created_at,
            expires_at=result.expires_at,
        )


@app.get("/api/v1/urls/{alias}")
async def redirect_short_url(alias: str) -> RedirectResponse:
    async with get_db_session() as session:
        service = UrlShortenerService(session)
        entity = await service.resolve_alias(alias)
        if entity is None:
            raise HTTPException(status_code=404, detail="Short URL not found")

        if entity.expires_at and entity.expires_at <= datetime.utcnow():
            raise HTTPException(status_code=410, detail="Short URL expired")

        await redis_client.lpush(
            "click_events",
            {
                "short_url_id": str(entity.id),
                "alias": entity.alias,
                "target_url": entity.original_url,
                "timestamp": datetime.utcnow().isoformat(),
            },
        )
        return RedirectResponse(url=entity.original_url, status_code=status.HTTP_307_TEMPORARY_REDIRECT)


@app.get("/api/v1/urls/{alias}/stats")
async def stats_for_url(alias: str) -> dict[str, Any]:
    async with get_db_session() as session:
        entity = await session.get(ShortUrl, alias)
        if entity is None:
            raise HTTPException(status_code=404, detail="Short URL not found")
        click_count = await session.scalar(
            __import__('sqlalchemy').select(__import__('sqlalchemy').func.count()).select_from(ClickEvent).where(ClickEvent.short_url_id == entity.id)
        )
        return {
            "alias": entity.alias,
            "original_url": entity.original_url,
            "total_clicks": click_count or 0,
            "created_at": entity.created_at.isoformat(),
            "expires_at": entity.expires_at.isoformat() if entity.expires_at else None,
        }


@app.get("/api/v1/analytics/summary")
async def summary() -> AnalyticsSummary:
    async with get_db_session() as session:
        total_urls = await session.scalar(__import__('sqlalchemy').select(__import__('sqlalchemy').func.count()).select_from(ShortUrl))
        active_urls = await session.scalar(
            __import__('sqlalchemy').select(__import__('sqlalchemy').func.count())
            .select_from(ShortUrl)
            .where((ShortUrl.expires_at.is_(None)) | (ShortUrl.expires_at > datetime.utcnow()))
        )
        total_clicks = await session.scalar(__import__('sqlalchemy').select(__import__('sqlalchemy').func.count()).select_from(ClickEvent))
        last_24h = await session.scalar(
            __import__('sqlalchemy').select(__import__('sqlalchemy').func.count())
            .select_from(ClickEvent)
            .where(ClickEvent.created_at >= datetime.utcnow() - timedelta(hours=24))
        )
        return AnalyticsSummary(
            total_urls=total_urls or 0,
            active_urls=active_urls or 0,
            total_clicks=total_clicks or 0,
            last_24h_clicks=last_24h or 0,
        )


# Orchestrator endpoints
@app.post("/api/v1/orchestrator/runs")
async def create_orchestrator_run(payload: dict[str, Any]) -> dict[str, Any]:
    name = payload.get("name", "default-run")
    nodes = payload.get("nodes", [])
    async with get_db_session() as session:
        run = OrchestrationRun(name=name, status="created")
        session.add(run)
        await session.commit()
        await session.refresh(run)

        for idx, node_payload in enumerate(nodes):
            dep = node_payload.get("depends_on")
            node = OrchestrationNode(
                run_id=run.id,
                name=node_payload.get("name", f"node-{idx}"),
                node_type=node_payload.get("type", "task"),
                status="pending",
                depends_on=dep,
                approval_required=bool(node_payload.get("approval_required", False)),
            )
            session.add(node)
        await session.commit()
        return {"run_id": str(run.id), "status": run.status, "node_count": len(nodes)}


@app.get("/api/v1/orchestrator/runs/{run_id}")
async def get_orchestrator_run(run_id: str) -> dict[str, Any]:
    async with get_db_session() as session:
        run = await session.get(OrchestrationRun, run_id)
        if run is None:
            raise HTTPException(status_code=404, detail="Run not found")
        nodes = (await session.execute(__import__('sqlalchemy').select(OrchestrationNode).where(OrchestrationNode.run_id == run_id))).scalars().all()
        return {
            "run_id": run.id,
            "name": run.name,
            "status": run.status,
            "nodes": [
                {
                    "id": node.id,
                    "name": node.name,
                    "type": node.node_type,
                    "status": node.status,
                    "depends_on": node.depends_on,
                    "approval_required": node.approval_required,
                    "approval_status": node.approval_status,
                }
                for node in nodes
            ],
        }


@app.post("/api/v1/orchestrator/runs/{run_id}/approve/{node_id}")
async def approve_orchestrator_node(run_id: str, node_id: str) -> dict[str, Any]:
    async with get_db_session() as session:
        node = await session.get(OrchestrationNode, node_id)
        if node is None or node.run_id != run_id:
            raise HTTPException(status_code=404, detail="Node not found")
        node.approval_status = "approved"
        node.status = "approved"
        await session.commit()
        return {"run_id": run_id, "node_id": node_id, "status": "approved"}


@app.post("/api/v1/orchestrator/runs/{run_id}/start")
async def start_orchestrator_run(run_id: str) -> dict[str, Any]:
    async with get_db_session() as session:
        run = await session.get(OrchestrationRun, run_id)
        if run is None:
            raise HTTPException(status_code=404, detail="Run not found")
        run.status = "running"
        await session.commit()

    # Simple orchestration simulation
    async with get_db_session() as session:
        nodes = (await session.execute(__import__('sqlalchemy').select(OrchestrationNode).where(OrchestrationNode.run_id == run_id))).scalars().all()
        if not nodes:
            run.status = "completed"
            await session.commit()
            return {"run_id": run_id, "status": "completed"}

        for node in nodes:
            if node.approval_required and node.approval_status != "approved":
                node.status = "awaiting_approval"
                run.status = "waiting_for_approval"
                await session.commit()
                continue
            node.status = "completed"
            await session.commit()

        run.status = "completed"
        await session.commit()

    return {"run_id": run_id, "status": "completed"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
