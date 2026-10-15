from __future__ import annotations

from datetime import datetime
from typing import Any

from sqlalchemy import String, DateTime, Text, JSON, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class OrchestrationRun(Base):
    __tablename__ = "orchestration_runs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: __import__('uuid').uuid4().hex)
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    status: Mapped[str] = mapped_column(String(32), default="created", nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    metadata: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)


class OrchestrationNode(Base):
    __tablename__ = "orchestration_nodes"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: __import__('uuid').uuid4().hex)
    run_id: Mapped[str] = mapped_column(String(36), ForeignKey("orchestration_runs.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    node_type: Mapped[str] = mapped_column(String(32), default="task", nullable=False)
    status: Mapped[str] = mapped_column(String(32), default="pending", nullable=False)
    depends_on: Mapped[str | None] = mapped_column(String(128), nullable=True)
    approval_required: Mapped[bool] = mapped_column(default=False, nullable=False)
    approval_status: Mapped[str] = mapped_column(String(32), default="pending", nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    last_error: Mapped[str | None] = mapped_column(Text, nullable=True)
