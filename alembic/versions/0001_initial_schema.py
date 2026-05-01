"""Redirect stub: the original 0001_initial_schema.py created a conflicting
schema (different table structures, no org_id PK). It has been superseded by
20260427_0001_phase1_core_models.py which is the authoritative initial schema.

This file is kept only so Alembic's revision graph doesn't break on existing
installations. It does nothing on upgrade/downgrade.

For a FRESH install: run `alembic upgrade head` — only 20260427_0001 runs.
For an EXISTING install that already ran 0001: run `alembic upgrade head`
  which will run the remaining migrations in the correct chain.

Revision ID: 0001
Revises: (none — root)
"""
from __future__ import annotations
from alembic import op
import sqlalchemy as sa

revision = '0001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # This migration is a no-op redirect.
    # The real schema is created by 20260427_0001_phase1_core_models.py
    pass


def downgrade() -> None:
    pass
