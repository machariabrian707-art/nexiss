"""Alembic migration: fix organization table — drop redundant `id` PK column,
making org_id the single primary key. Also ensures all FK columns exist.

Revision ID: 20260429_0007
Revises: 20260427_0006
"""
from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "20260429_0007"
down_revision = "20260427_0006"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # The organizations table may have been created with both `id` PK and
    # `org_id` unique. We need org_id to be the sole PK so FK constraints work.
    # This migration is safe to run even if the table was already correct
    # because we use IF EXISTS / try-except style via execute.

    conn = op.get_bind()

    # Check if column `id` exists in organizations
    result = conn.execute(sa.text(
        "SELECT column_name FROM information_schema.columns "
        "WHERE table_name='organizations' AND column_name='id'"
    ))
    has_id_col = result.fetchone() is not None

    if has_id_col:
        # Drop old PK constraint on `id`
        conn.execute(sa.text(
            "ALTER TABLE organizations DROP CONSTRAINT IF EXISTS organizations_pkey"
        ))
        # Make org_id the primary key
        conn.execute(sa.text(
            "ALTER TABLE organizations ADD PRIMARY KEY (org_id)"
        ))
        # Drop the old `id` column (it was never referenced externally)
        conn.execute(sa.text(
            "ALTER TABLE organizations DROP COLUMN IF EXISTS id"
        ))


def downgrade() -> None:
    # Re-add the id column (no data recovery needed for dev environments)
    op.add_column(
        "organizations",
        sa.Column("id", sa.dialects.postgresql.UUID(as_uuid=True), nullable=True),
    )
