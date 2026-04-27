from nexiss.db.base import Base
from nexiss.db.models import (
    automation,
    billing,
    document,
    org_membership,
    organization,
    processing_job,
    usage_event,
    user,
)


def test_core_tables_registered() -> None:
    _ = (automation, billing, document, org_membership, organization, processing_job, usage_event, user)
    table_names = set(Base.metadata.tables.keys())

    assert "organizations" in table_names
    assert "users" in table_names
    assert "org_memberships" in table_names
    assert "documents" in table_names
    assert "processing_jobs" in table_names
    assert "automation_rules" in table_names
    assert "automation_runs" in table_names
    assert "billing_customers" in table_names
    assert "billing_subscriptions" in table_names
    assert "usage_events" in table_names
