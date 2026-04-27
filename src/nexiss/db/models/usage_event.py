from __future__ import annotations

import enum
import uuid
from datetime import datetime
from decimal import Decimal

from sqlalchemy import BigInteger, DateTime, Enum, ForeignKey, Numeric, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from nexiss.db.base import Base


class UsageMetricType(str, enum.Enum):
    document_processed = "document_processed"
    page_processed = "page_processed"
    storage_bytes = "storage_bytes"
    llm_tokens_input = "llm_tokens_input"
    llm_tokens_output = "llm_tokens_output"


class UsageEvent(Base):
    __tablename__ = "usage_events"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    org_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("organizations.org_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    document_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("documents.id", ondelete="SET NULL"), nullable=True, index=True
    )
    metric_type: Mapped[UsageMetricType] = mapped_column(
        Enum(UsageMetricType, name="usage_metric_type"), nullable=False
    )
    quantity: Mapped[int] = mapped_column(BigInteger, nullable=False)
    unit_cost: Mapped[Decimal | None] = mapped_column(Numeric(12, 6), nullable=True)
    total_cost: Mapped[Decimal | None] = mapped_column(Numeric(14, 6), nullable=True)
    details: Mapped[dict | None] = mapped_column("metadata", JSONB, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False, index=True
    )
