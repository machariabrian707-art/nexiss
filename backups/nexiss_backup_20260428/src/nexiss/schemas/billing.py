from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from nexiss.db.models.billing import BillingSubscriptionStatus


class BillingStatusResponse(BaseModel):
    org_id: UUID
    has_customer: bool
    stripe_customer_id: str | None
    has_subscription: bool
    stripe_subscription_id: str | None
    subscription_status: BillingSubscriptionStatus | None
    current_period_end: datetime | None
    cancel_at_period_end: bool | None
