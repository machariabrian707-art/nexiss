"""phase 7 progress tracking jobs

Revision ID: 20260427_0003
Revises: 20260427_0002
Create Date: 2026-04-27 05:58:00
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "20260427_0003"
down_revision: str | None = "20260427_0002"
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None


processing_job_status = postgresql.ENUM(
    "queued", "running", "completed", "failed", name="processing_job_status", create_type=False
)


def upgrade() -> None:
    processing_job_status.create(op.get_bind(), checkfirst=True)

    op.create_table(
        "processing_jobs",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("org_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("document_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("task_id", sa.String(length=128), nullable=False),
        sa.Column("status", processing_job_status, nullable=False),
        sa.Column("progress_percentage", sa.Integer(), nullable=False, server_default=sa.text("0")),
        sa.Column("current_step", sa.String(length=120), nullable=False),
        sa.Column("error_message", sa.String(length=1024), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(
            ["org_id"], ["organizations.org_id"], name="fk_processing_jobs_org_id_organizations", ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(
            ["document_id"], ["documents.id"], name="fk_processing_jobs_document_id_documents", ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id", name="pk_processing_jobs"),
        sa.UniqueConstraint("task_id", name="uq_processing_jobs_task_id"),
    )
    op.create_index("ix_processing_jobs_org_id", "processing_jobs", ["org_id"], unique=False)
    op.create_index("ix_processing_jobs_document_id", "processing_jobs", ["document_id"], unique=False)
    op.create_index("ix_processing_jobs_task_id", "processing_jobs", ["task_id"], unique=False)
    op.alter_column("processing_jobs", "progress_percentage", server_default=None)


def downgrade() -> None:
    op.drop_index("ix_processing_jobs_task_id", table_name="processing_jobs")
    op.drop_index("ix_processing_jobs_document_id", table_name="processing_jobs")
    op.drop_index("ix_processing_jobs_org_id", table_name="processing_jobs")
    op.drop_table("processing_jobs")
    processing_job_status.drop(op.get_bind(), checkfirst=True)
