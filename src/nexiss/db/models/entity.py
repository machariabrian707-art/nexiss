"""Entity registry: named real-world things extracted from documents.

Examples: a patient named 'John Mwangi', a vendor named 'Doshi Hardware',
an employee named 'Grace Wanjiku'. Entities allow cross-document search:
  GET /search?q=Doshi&doc_type=invoice  -> all invoices from Doshi
  GET /search?q=John+Mwangi&doc_type=patient_record -> all records for that patient
"""
from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Text, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from nexiss.db.base import Base


class Entity(Base):
    __tablename__ = "entities"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    org_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("organizations.org_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    # canonical name, e.g. "Doshi Hardware Ltd"
    canonical_name: Mapped[str] = mapped_column(String(512), nullable=False)
    # entity kind: person | organization | place | product | other
    entity_kind: Mapped[str] = mapped_column(String(64), nullable=False, default="unknown")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    __table_args__ = (
        UniqueConstraint("org_id", "canonical_name", "entity_kind", name="uq_entity_org_name_kind"),
    )


class EntityAlias(Base):
    """Alternative spellings / nicknames for an Entity (supports fuzzy matching)."""
    __tablename__ = "entity_aliases"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    entity_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("entities.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    alias: Mapped[str] = mapped_column(String(512), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    __table_args__ = (
        UniqueConstraint("entity_id", "alias", name="uq_entity_alias"),
    )


class DocumentEntity(Base):
    """Links a document to one or more entities extracted from it."""
    __tablename__ = "document_entities"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    org_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("organizations.org_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    document_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("documents.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    entity_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("entities.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    # role this entity plays in the document: patient, vendor, employee, party_a, etc.
    role: Mapped[str | None] = mapped_column(String(128), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    __table_args__ = (
        UniqueConstraint("document_id", "entity_id", "role", name="uq_doc_entity_role"),
    )
