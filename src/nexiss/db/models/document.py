from __future__ import annotations

import enum
import uuid
from datetime import datetime
from decimal import Decimal

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, Numeric, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from nexiss.db.base import Base
from nexiss.db.models.document_type import DocumentType


class DocumentStatus(str, enum.Enum):
    uploaded = "uploaded"
    processing = "processing"
    completed = "completed"
    failed = "failed"


class Document(Base):
    __tablename__ = "documents"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    org_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("organizations.org_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    created_by_user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True
    )
    file_name: Mapped[str] = mapped_column(String(255), nullable=False)
    content_type: Mapped[str] = mapped_column(String(100), nullable=False)
    storage_key: Mapped[str] = mapped_column(String(1024), nullable=False, unique=True)
    status: Mapped[DocumentStatus] = mapped_column(
        Enum(DocumentStatus, name="document_status"), nullable=False, default=DocumentStatus.uploaded
    )
    # -- Classification fields (core to Nexiss product) --
    # declared_type: what the uploader says this document is
    declared_type: Mapped[str | None] = mapped_column(
        String(64), nullable=True, index=True,
        comment="Document type declared by the uploader before processing"
    )
    # confirmed_type: what the AI pipeline confirmed after extraction
    confirmed_type: Mapped[str | None] = mapped_column(
        String(64), nullable=True, index=True,
        comment="Document type confirmed by the AI classification pipeline"
    )
    # type_confidence: how sure the AI is about the confirmed_type
    type_confidence: Mapped[Decimal | None] = mapped_column(
        Numeric(5, 4), nullable=True,
        comment="Confidence score for confirmed_type classification"
    )
    # -- Extraction fields --
    page_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    extracted_data: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    confidence_score: Mapped[Decimal | None] = mapped_column(Numeric(5, 4), nullable=True)
    processing_attempts: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default="0")
    last_error: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    # -- Timestamps --
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )
