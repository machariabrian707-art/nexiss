"""phase 6 document lifecycle fields

Revision ID: 20260427_0002
Revises: 20260427_0001
Create Date: 2026-04-27 05:40:00
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "20260427_0002"
down_revision: str | None = "20260427_0001"
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "documents",
        sa.Column("processing_attempts", sa.Integer(), nullable=False, server_default=sa.text("0")),
    )
    op.add_column("documents", sa.Column("last_error", sa.String(length=1024), nullable=True))
    op.alter_column("documents", "processing_attempts", server_default=None)


def downgrade() -> None:
    op.drop_column("documents", "last_error")
    op.drop_column("documents", "processing_attempts")
