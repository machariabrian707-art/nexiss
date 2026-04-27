"""phase 9 internal automation engine

Revision ID: 20260427_0004
Revises: 20260427_0003
Create Date: 2026-04-27 06:10:00
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "20260427_0004"
down_revision: str | None = "20260427_0003"
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None


automation_trigger_type = postgresql.ENUM(
    "document_processed", name="automation_trigger_type", create_type=False
)
automation_run_status = postgresql.ENUM(
    "succeeded", "failed", name="automation_run_status", create_type=False
)


def upgrade() -> None:
    automation_trigger_type.create(op.get_bind(), checkfirst=True)
    automation_run_status.create(op.get_bind(), checkfirst=True)

    op.create_table(
        "automation_rules",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("org_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(length=160), nullable=False),
        sa.Column("is_enabled", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("trigger_type", automation_trigger_type, nullable=False),
        sa.Column("conditions", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("actions", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(
            ["org_id"], ["organizations.org_id"], name="fk_automation_rules_org_id_organizations", ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id", name="pk_automation_rules"),
    )
    op.create_index("ix_automation_rules_org_id", "automation_rules", ["org_id"], unique=False)
    op.alter_column("automation_rules", "is_enabled", server_default=None)

    op.create_table(
        "automation_runs",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("org_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("rule_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("document_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("trigger_type", automation_trigger_type, nullable=False),
        sa.Column("status", automation_run_status, nullable=False),
        sa.Column("action_count", sa.Integer(), nullable=False, server_default=sa.text("0")),
        sa.Column("error_message", sa.String(length=1024), nullable=True),
        sa.Column("executed_actions", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(
            ["org_id"], ["organizations.org_id"], name="fk_automation_runs_org_id_organizations", ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(
            ["rule_id"], ["automation_rules.id"], name="fk_automation_runs_rule_id_automation_rules", ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(
            ["document_id"], ["documents.id"], name="fk_automation_runs_document_id_documents", ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id", name="pk_automation_runs"),
    )
    op.create_index("ix_automation_runs_org_id", "automation_runs", ["org_id"], unique=False)
    op.create_index("ix_automation_runs_rule_id", "automation_runs", ["rule_id"], unique=False)
    op.create_index("ix_automation_runs_document_id", "automation_runs", ["document_id"], unique=False)
    op.alter_column("automation_runs", "action_count", server_default=None)


def downgrade() -> None:
    op.drop_index("ix_automation_runs_document_id", table_name="automation_runs")
    op.drop_index("ix_automation_runs_rule_id", table_name="automation_runs")
    op.drop_index("ix_automation_runs_org_id", table_name="automation_runs")
    op.drop_table("automation_runs")

    op.drop_index("ix_automation_rules_org_id", table_name="automation_rules")
    op.drop_table("automation_rules")

    automation_run_status.drop(op.get_bind(), checkfirst=True)
    automation_trigger_type.drop(op.get_bind(), checkfirst=True)
