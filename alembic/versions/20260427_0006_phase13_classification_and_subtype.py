"""Phase 13/14: document subtype column + superuser admin migration.

Revision ID: 20260427_0006
Revises: 20260427_0005
Create Date: 2026-04-27
"""
from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "20260427_0006"
down_revision = "20260427_0005"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add document_subtype to documents table
    # (declared_type, confirmed_type, type_confidence already added in 0003)
    op.add_column(
        "documents",
        sa.Column("document_subtype", sa.String(64), nullable=True),
    )
    op.create_index("ix_documents_document_subtype", "documents", ["document_subtype"])

    # Ensure users.is_superuser exists (may have been added earlier but guard with try)
    # Using server_default=false so existing rows default to non-admin
    try:
        op.add_column(
            "users",
            sa.Column(
                "is_superuser",
                sa.Boolean(),
                nullable=False,
                server_default=sa.false(),
            ),
        )
    except Exception:
        pass  # column already exists, safe to skip


def downgrade() -> None:
    op.drop_index("ix_documents_document_subtype", table_name="documents")
    op.drop_column("documents", "document_subtype")
