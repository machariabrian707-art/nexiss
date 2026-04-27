"""phase 1 core models

Revision ID: 20260427_0001
Revises:
Create Date: 2026-04-27 01:00:00
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "20260427_0001"
down_revision: str | None = None
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None


membership_role = postgresql.ENUM(
    "owner", "admin", "member", "reviewer", name="membership_role", create_type=False
)
membership_status = postgresql.ENUM(
    "active", "invited", "suspended", name="membership_status", create_type=False
)
document_status = postgresql.ENUM(
    "uploaded", "processing", "completed", "failed", name="document_status", create_type=False
)
usage_metric_type = postgresql.ENUM(
    "document_processed",
    "page_processed",
    "storage_bytes",
    "llm_tokens_input",
    "llm_tokens_output",
    name="usage_metric_type",
    create_type=False,
)


def upgrade() -> None:
    membership_role.create(op.get_bind(), checkfirst=True)
    membership_status.create(op.get_bind(), checkfirst=True)
    document_status.create(op.get_bind(), checkfirst=True)
    usage_metric_type.create(op.get_bind(), checkfirst=True)

    op.create_table(
        "organizations",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("org_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("slug", sa.String(length=120), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id", name="pk_organizations"),
        sa.UniqueConstraint("org_id", name="uq_organizations_org_id"),
        sa.UniqueConstraint("slug", name="uq_organizations_slug"),
    )
    op.create_index("ix_organizations_org_id", "organizations", ["org_id"], unique=False)
    op.create_index("ix_organizations_slug", "organizations", ["slug"], unique=False)

    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("org_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("email", sa.String(length=320), nullable=False),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column("full_name", sa.String(length=255), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("is_superuser", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["org_id"], ["organizations.org_id"], name="fk_users_org_id_organizations"),
        sa.PrimaryKeyConstraint("id", name="pk_users"),
        sa.UniqueConstraint("email", name="uq_users_email"),
    )
    op.create_index("ix_users_email", "users", ["email"], unique=False)
    op.create_index("ix_users_org_id", "users", ["org_id"], unique=False)

    op.create_table(
        "org_memberships",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("org_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("role", membership_role, nullable=False),
        sa.Column("status", membership_status, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(
            ["org_id"], ["organizations.org_id"], name="fk_org_memberships_org_id_organizations"
        ),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], name="fk_org_memberships_user_id_users"),
        sa.PrimaryKeyConstraint("id", name="pk_org_memberships"),
        sa.UniqueConstraint("org_id", "user_id", name="uq_org_membership_org_user"),
    )
    op.create_index("ix_org_memberships_org_id", "org_memberships", ["org_id"], unique=False)
    op.create_index("ix_org_memberships_user_id", "org_memberships", ["user_id"], unique=False)

    op.create_table(
        "documents",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("org_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("created_by_user_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("file_name", sa.String(length=255), nullable=False),
        sa.Column("content_type", sa.String(length=100), nullable=False),
        sa.Column("storage_key", sa.String(length=1024), nullable=False),
        sa.Column("status", document_status, nullable=False),
        sa.Column("page_count", sa.Integer(), nullable=True),
        sa.Column("extracted_data", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("confidence_score", sa.Numeric(precision=5, scale=4), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(
            ["created_by_user_id"], ["users.id"], name="fk_documents_created_by_user_id_users", ondelete="SET NULL"
        ),
        sa.ForeignKeyConstraint(
            ["org_id"], ["organizations.org_id"], name="fk_documents_org_id_organizations", ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id", name="pk_documents"),
        sa.UniqueConstraint("storage_key", name="uq_documents_storage_key"),
    )
    op.create_index("ix_documents_created_by_user_id", "documents", ["created_by_user_id"], unique=False)
    op.create_index("ix_documents_org_id", "documents", ["org_id"], unique=False)

    op.create_table(
        "usage_events",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("org_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("document_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("metric_type", usage_metric_type, nullable=False),
        sa.Column("quantity", sa.BigInteger(), nullable=False),
        sa.Column("unit_cost", sa.Numeric(precision=12, scale=6), nullable=True),
        sa.Column("total_cost", sa.Numeric(precision=14, scale=6), nullable=True),
        sa.Column("metadata", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(
            ["document_id"], ["documents.id"], name="fk_usage_events_document_id_documents", ondelete="SET NULL"
        ),
        sa.ForeignKeyConstraint(
            ["org_id"], ["organizations.org_id"], name="fk_usage_events_org_id_organizations", ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id", name="pk_usage_events"),
    )
    op.create_index("ix_usage_events_created_at", "usage_events", ["created_at"], unique=False)
    op.create_index("ix_usage_events_document_id", "usage_events", ["document_id"], unique=False)
    op.create_index("ix_usage_events_org_id", "usage_events", ["org_id"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_usage_events_org_id", table_name="usage_events")
    op.drop_index("ix_usage_events_document_id", table_name="usage_events")
    op.drop_index("ix_usage_events_created_at", table_name="usage_events")
    op.drop_table("usage_events")

    op.drop_index("ix_documents_org_id", table_name="documents")
    op.drop_index("ix_documents_created_by_user_id", table_name="documents")
    op.drop_table("documents")

    op.drop_index("ix_org_memberships_user_id", table_name="org_memberships")
    op.drop_index("ix_org_memberships_org_id", table_name="org_memberships")
    op.drop_table("org_memberships")

    op.drop_index("ix_users_org_id", table_name="users")
    op.drop_index("ix_users_email", table_name="users")
    op.drop_table("users")

    op.drop_index("ix_organizations_slug", table_name="organizations")
    op.drop_index("ix_organizations_org_id", table_name="organizations")
    op.drop_table("organizations")

    usage_metric_type.drop(op.get_bind(), checkfirst=True)
    document_status.drop(op.get_bind(), checkfirst=True)
    membership_status.drop(op.get_bind(), checkfirst=True)
    membership_role.drop(op.get_bind(), checkfirst=True)
