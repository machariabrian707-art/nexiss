from __future__ import annotations

from datetime import UTC, datetime
from uuid import UUID

from fastapi import APIRouter, Depends, Header, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from nexiss.api.deps.auth import AuthContext, require_org_context
from nexiss.core.config import get_settings
from nexiss.db.models.billing import BillingCustomer, BillingSubscription, BillingSubscriptionStatus
from nexiss.db.session import get_db_session
from nexiss.schemas.billing import BillingStatusResponse
from nexiss.services.billing.stripe_service import verify_and_construct_event

router = APIRouter(prefix="/billing", tags=["billing"])
settings = get_settings()


@router.get("/status", response_model=BillingStatusResponse)
async def get_billing_status(
    auth: AuthContext = Depends(require_org_context),
    db: AsyncSession = Depends(get_db_session),
) -> BillingStatusResponse:
    customer_row = await db.execute(select(BillingCustomer).where(BillingCustomer.org_id == auth.active_org_id))
    customer = customer_row.scalar_one_or_none()

    subscription_row = await db.execute(
        select(BillingSubscription)
        .where(BillingSubscription.org_id == auth.active_org_id)
        .order_by(BillingSubscription.created_at.desc())
        .limit(1)
    )
    subscription = subscription_row.scalar_one_or_none()

    return BillingStatusResponse(
        org_id=auth.active_org_id,
        has_customer=customer is not None,
        stripe_customer_id=customer.stripe_customer_id if customer else None,
        has_subscription=subscription is not None,
        stripe_subscription_id=subscription.stripe_subscription_id if subscription else None,
        subscription_status=subscription.status if subscription else None,
        current_period_end=subscription.current_period_end if subscription else None,
        cancel_at_period_end=subscription.cancel_at_period_end if subscription else None,
    )


@router.post("/stripe/webhook", status_code=status.HTTP_204_NO_CONTENT)
async def stripe_webhook(
    request: Request,
    stripe_signature: str | None = Header(default=None, alias="Stripe-Signature"),
    db: AsyncSession = Depends(get_db_session),
) -> None:
    if settings.billing_provider != "stripe":
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Billing provider is not enabled",
        )
    if not stripe_signature:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Missing Stripe-Signature header")

    payload = await request.body()
    try:
        event = verify_and_construct_event(payload=payload, signature_header=stripe_signature)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc)) from exc
    except Exception:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid webhook signature")

    if event["type"] == "customer.created":
        customer_id = event["data"]["object"]["id"]
        metadata = event["data"]["object"].get("metadata") or {}
        org_id_raw = metadata.get("org_id")
        if org_id_raw:
            try:
                org_id = UUID(org_id_raw)
            except ValueError:
                return
            existing = await db.execute(
                select(BillingCustomer).where(BillingCustomer.stripe_customer_id == customer_id)
            )
            if existing.scalar_one_or_none() is None:
                db.add(BillingCustomer(org_id=org_id, stripe_customer_id=customer_id))
                await db.commit()

    if event["type"] in {"customer.subscription.created", "customer.subscription.updated"}:
        sub = event["data"]["object"]
        subscription_id = sub["id"]
        metadata = sub.get("metadata") or {}
        org_id_raw = metadata.get("org_id")
        if org_id_raw:
            try:
                org_id = UUID(org_id_raw)
            except ValueError:
                return
            status_raw = sub.get("status", "incomplete")
            try:
                status_value = BillingSubscriptionStatus(status_raw)
            except ValueError:
                status_value = BillingSubscriptionStatus.incomplete

            current_period_end = sub.get("current_period_end")
            period_end_dt = (
                datetime.fromtimestamp(int(current_period_end), tz=UTC) if current_period_end else None
            )
            existing = await db.execute(
                select(BillingSubscription).where(BillingSubscription.stripe_subscription_id == subscription_id)
            )
            row = existing.scalar_one_or_none()
            if row is None:
                db.add(
                    BillingSubscription(
                        org_id=org_id,
                        stripe_subscription_id=subscription_id,
                        status=status_value,
                        current_period_end=period_end_dt,
                        cancel_at_period_end=bool(sub.get("cancel_at_period_end", False)),
                    )
                )
            else:
                row.status = status_value
                row.current_period_end = period_end_dt
                row.cancel_at_period_end = bool(sub.get("cancel_at_period_end", False))
            await db.commit()
