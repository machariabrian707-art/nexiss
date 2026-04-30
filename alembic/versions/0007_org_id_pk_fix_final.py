"""org_id PK fix final

Revision ID: 0007
Revises: e35404209ae5
Create Date: 2026-04-29

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0007'
down_revision = 'e35404209ae5'
branch_labels = None
depends_on = None

TABLES_WITH_ORG_ID = [
    "users",
    "documents",
    "usage_events",
    "processing_jobs",
    "automation_rules",
    "automation_runs",
    "billing_customers",
    "billing_subscriptions",
    "entities",
    "document_entities",
    "org_memberships"
]

def upgrade() -> None:
    # 1. Drop existing foreign keys
    for table in TABLES_WITH_ORG_ID:
        try:
            op.drop_constraint(f'fk_{table}_org_id_organizations', table, type_='foreignkey')
        except Exception:
            pass

    # 2. Fix organizations primary key
    # Drop existing PK constraint
    try:
        op.drop_constraint('pk_organizations', 'organizations', type_='primary')
    except Exception:
        pass
    
    # Drop unique constraint on org_id if it exists (we will make it PK)
    try:
        op.drop_constraint('uq_organizations_org_id', 'organizations', type_='unique')
    except Exception:
        pass

    # Add PK constraint to org_id
    op.create_primary_key('pk_organizations', 'organizations', ['org_id'])

    # 3. Recreate foreign keys pointing to organizations.org_id
    for table in TABLES_WITH_ORG_ID:
        op.create_foreign_key(
            f'fk_{table}_org_id_organizations',
            table, 'organizations',
            ['org_id'], ['org_id'],
            ondelete='CASCADE'
        )


def downgrade() -> None:
    for table in TABLES_WITH_ORG_ID:
        op.drop_constraint(f'fk_{table}_org_id_organizations', table, type_='foreignkey')

    op.drop_constraint('pk_organizations', 'organizations', type_='primary')
    op.create_primary_key('pk_organizations', 'organizations', ['id'])
    op.create_unique_constraint('uq_organizations_org_id', 'organizations', ['org_id'])

    for table in TABLES_WITH_ORG_ID:
        # Note: this might be wrong if they originally pointed to 'id', 
        # but in most cases they used 'org_id' column to point to 'org_id' column (even if it wasn't PK)
        op.create_foreign_key(
            f'fk_{table}_org_id_organizations',
            table, 'organizations',
            ['org_id'], ['org_id'],
            ondelete='CASCADE'
        )
