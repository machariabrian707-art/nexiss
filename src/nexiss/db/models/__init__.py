"""DB model imports — all models must be imported here so Alembic can discover them."""
from nexiss.db.models.automation import AutomationRule, AutomationRun  # noqa: F401
from nexiss.db.models.billing import BillingCustomer, BillingSubscription  # noqa: F401
from nexiss.db.models.classification import DocumentCategory  # noqa: F401
from nexiss.db.models.document import Document, DocumentStatus  # noqa: F401
from nexiss.db.models.entity import DocumentEntity, Entity, EntityAlias  # noqa: F401
from nexiss.db.models.org_membership import OrgMembership, MembershipRole as OrgRole  # noqa: F401
from nexiss.db.models.organization import Organization  # noqa: F401
from nexiss.db.models.processing_job import ProcessingJob, ProcessingJobStatus  # noqa: F401
from nexiss.db.models.usage_event import UsageEvent, UsageMetricType  # noqa: F401
from nexiss.db.models.user import User  # noqa: F401

__all__ = [
    "AutomationRule",
    "AutomationRun",
    "BillingCustomer",
    "BillingSubscription",
    "Document",
    "DocumentCategory",
    "DocumentEntity",
    "DocumentStatus",
    "Entity",
    "EntityAlias",
    "OrgMembership",
    "OrgRole",
    "Organization",
    "ProcessingJob",
    "ProcessingJobStatus",
    "UsageEvent",
    "UsageMetricType",
    "User",
]
