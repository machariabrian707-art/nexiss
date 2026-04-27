"""document classification and entity registry

Revision ID: 20260427_0003
Revises: 20260427_0002
Create Date: 2026-04-27
"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa

revision = "20260427_0003"
down_revision = "20260427_0002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add classification columns to documents
    op.add_column("documents", sa.Column("declared_type", sa.String(64), nullable=True))
    op.add_column("documents", sa.Column("confirmed_type", sa.String(64), nullable=True))
    op.add_column("documents", sa.Column("type_confidence", sa.Numeric(5, 4), nullable=True))
    op.create_index("ix_documents_declared_type", "documents", ["declared_type"])
    op.create_index("ix_documents_confirmed_type", "documents", ["confirmed_type"])

    # Entity registry
    op.create_table(
        "entities",
        sa.Column("id", sa.dialects.postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("org_id", sa.dialects.postgresql.UUID(as_uuid=True), sa.ForeignKey("organizations.org_id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("canonical_name", sa.String(512), nullable=False),
        sa.Column("entity_kind", sa.String(64), nullable=False, server_default="unknown"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("org_id", "canonical_name", "entity_kind", name="uq_entity_org_name_kind"),
    )

    op.create_table(
        "entity_aliases",
        sa.Column("id", sa.dialects.postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("entity_id", sa.dialects.postgresql.UUID(as_uuid=True), sa.ForeignKey("entities.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("alias", sa.String(512), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("entity_id", "alias", name="uq_entity_alias"),
    )

    op.create_table(
        "document_entities",
        sa.Column("id", sa.dialects.postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("org_id", sa.dialects.postgresql.UUID(as_uuid=True), sa.ForeignKey("organizations.org_id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("document_id", sa.dialects.postgresql.UUID(as_uuid=True), sa.ForeignKey("documents.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("entity_id", sa.dialects.postgresql.UUID(as_uuid=True), sa.ForeignKey("entities.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("role", sa.String(128), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("document_id", "entity_id", "role", name="uq_doc_entity_role"),
    )


def downgrade() -> None:
    op.drop_table("document_entities")
    op.drop_table("entity_aliases")
    op.drop_table("entities")
    op.drop_index("ix_documents_confirmed_type", table_name="documents")
    op.drop_index("ix_documents_declared_type", table_name="documents")
    op.drop_column("documents", "type_confidence")
    op.drop_column("documents", "confirmed_type")
    op.drop_column("documents", "declared_type")
