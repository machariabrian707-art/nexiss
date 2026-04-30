"""phase 11 billing (stripe-ready)

Revision ID: 20260427_0005
Revises: 20260427_0004
Create Date: 2026-04-27 06:45:00
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "20260427_0005"
down_revision: str | None = "20260427_0004"
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None


billing_subscription_status = postgresql.ENUM(
    "active",
    "trialing",
    "past_due",
    "canceled",
    "incomplete",
    "unpaid",
    name="billing_subscription_status",
    create_type=False,
)


def upgrade() -> None:
    billing_subscription_status.create(op.get_bind(), checkfirst=True)

    op.create_table(
        "billing_customers",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("org_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("stripe_customer_id", sa.String(length=128), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(
            ["org_id"], ["organizations.org_id"], name="fk_billing_customers_org_id_organizations", ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id", name="pk_billing_customers"),
        sa.UniqueConstraint("org_id", name="uq_billing_customers_org_id"),
        sa.UniqueConstraint("stripe_customer_id", name="uq_billing_customers_stripe_customer_id"),
    )
    op.create_index("ix_billing_customers_org_id", "billing_customers", ["org_id"], unique=False)
    op.create_index(
        "ix_billing_customers_stripe_customer_id",
        "billing_customers",
        ["stripe_customer_id"],
        unique=False,
    )
    op.alter_column("billing_customers", "is_active", server_default=None)

    op.create_table(
        "billing_subscriptions",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("org_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("stripe_subscription_id", sa.String(length=128), nullable=False),
        sa.Column("status", billing_subscription_status, nullable=False),
        sa.Column("current_period_end", sa.DateTime(timezone=True), nullable=True),
        sa.Column("cancel_at_period_end", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(
            ["org_id"], ["organizations.org_id"], name="fk_billing_subscriptions_org_id_organizations", ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id", name="pk_billing_subscriptions"),
        sa.UniqueConstraint(
            "stripe_subscription_id", name="uq_billing_subscriptions_stripe_subscription_id"
        ),
    )
    op.create_index("ix_billing_subscriptions_org_id", "billing_subscriptions", ["org_id"], unique=False)
    op.create_index(
        "ix_billing_subscriptions_stripe_subscription_id",
        "billing_subscriptions",
        ["stripe_subscription_id"],
        unique=False,
    )
    op.alter_column("billing_subscriptions", "cancel_at_period_end", server_default=None)


def downgrade() -> None:
    op.drop_index("ix_billing_subscriptions_stripe_subscription_id", table_name="billing_subscriptions")
    op.drop_index("ix_billing_subscriptions_org_id", table_name="billing_subscriptions")
    op.drop_table("billing_subscriptions")

    op.drop_index("ix_billing_customers_stripe_customer_id", table_name="billing_customers")
    op.drop_index("ix_billing_customers_org_id", table_name="billing_customers")
    op.drop_table("billing_customers")

    billing_subscription_status.drop(op.get_bind(), checkfirst=True)
