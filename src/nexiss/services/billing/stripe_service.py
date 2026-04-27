from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from nexiss.core.config import get_settings

settings = get_settings()

if TYPE_CHECKING:
    import stripe  # pragma: no cover


@dataclass(slots=True)
class StripeWebhookConfig:
    secret: str


def _require_stripe_webhook_secret() -> StripeWebhookConfig:
    if not settings.stripe_webhook_secret:
        raise ValueError("STRIPE_WEBHOOK_SECRET is not configured")
    return StripeWebhookConfig(secret=settings.stripe_webhook_secret)


def verify_and_construct_event(*, payload: bytes, signature_header: str) -> Any:
    cfg = _require_stripe_webhook_secret()
    try:
        import stripe  # type: ignore
    except ModuleNotFoundError as exc:
        raise RuntimeError("Stripe SDK not installed. Install the 'stripe' package.") from exc
    return stripe.Webhook.construct_event(payload=payload, sig_header=signature_header, secret=cfg.secret)
