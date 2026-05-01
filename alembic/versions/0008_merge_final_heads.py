"""Single authoritative migration head.

Merges the two parallel chains that existed in the repo:
  - 0007 (org_id PK fix final, from 0007_org_id_pk_fix_final.py)
  - 20260429_0007 (fix_organization_primary_key)

Both chains do the same thing — this merge makes Alembic happy with one head.

Revision ID: 0008_merge_final_heads
Revises: 0007, 20260429_0007
"""
from __future__ import annotations
from alembic import op

revision = '0008_merge_final_heads'
down_revision = ('0007', '20260429_0007')
branch_labels = None
depends_on = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
