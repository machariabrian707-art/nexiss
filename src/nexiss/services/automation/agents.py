from __future__ import annotations

import logging
from typing import Any, Protocol

from sqlalchemy import select
from sqlalchemy.orm import Session

from nexiss.db.models.billing import BillingSubscription, BillingSubscriptionStatus
from nexiss.db.models.document import Document

logger = logging.getLogger(__name__)


class AutomationAgent(Protocol):
    def __call__(self, db: Session, document: Document, action_params: dict[str, Any]) -> dict[str, Any]:
        ...


def payment_agent(db: Session, document: Document, action_params: dict[str, Any]) -> dict[str, Any]:
    """Agent that verifies if the organization has an active subscription."""
    logger.info(f"PaymentAgent checking subscription for org {document.org_id}")
    
    sub = db.execute(
        select(BillingSubscription).where(
            BillingSubscription.org_id == document.org_id,
            BillingSubscription.status == BillingSubscriptionStatus.active
        )
    ).scalar_one_or_none()
    
    if sub:
        return {"status": "success", "agent": "PaymentAgent", "message": "Active subscription found"}
    else:
        return {"status": "failed", "agent": "PaymentAgent", "error": "No active subscription found"}


def verification_agent(db: Session, document: Document, action_params: dict[str, Any]) -> dict[str, Any]:
    """Agent that checks document confidence levels and flags for manual review if low."""
    confidence = document.type_confidence or 0.0
    threshold = action_params.get("threshold", 0.8)
    
    if confidence < threshold:
        # Flag for manual review - assuming Document has a status or meta_data field for this
        meta = document.meta_data or {}
        document.meta_data = {**meta, "needs_manual_review": True, "review_reason": f"Low confidence: {confidence}"}
        return {
            "status": "success", 
            "agent": "VerificationAgent", 
            "message": f"Document flagged for review (confidence {confidence} < {threshold})"
        }
    
    return {"status": "success", "agent": "VerificationAgent", "message": "Verification passed"}


def extraction_agent(db: Session, document: Document, action_params: dict[str, Any]) -> dict[str, Any]:
    """Agent that performs post-extraction data enrichment or validation."""
    # Example: Ensure specific fields exist in extracted_data
    required_fields = action_params.get("required_fields", [])
    data = document.extracted_data or {}
    
    missing = [f for f in required_fields if f not in data]
    if missing:
        return {
            "status": "failed", 
            "agent": "ExtractionAgent", 
            "error": f"Missing required fields: {', '.join(missing)}"
        }
        
    return {"status": "success", "agent": "ExtractionAgent", "message": "Extraction validation passed"}


# Registry of available agents
AGENT_REGISTRY: dict[str, AutomationAgent] = {
    "payment_agent": payment_agent,
    "verification_agent": verification_agent,
    "extraction_agent": extraction_agent,
}
