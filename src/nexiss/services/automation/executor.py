from __future__ import annotations

import logging
from typing import Any

import httpx
from sqlalchemy.orm import Session

from nexiss.db.models.automation import AutomationRule
from nexiss.db.models.document import Document
from nexiss.services.automation.agents import AGENT_REGISTRY

logger = logging.getLogger(__name__)


def execute_action(
    db: Session,
    rule: AutomationRule,
    document: Document,
    action: dict[str, Any],
) -> dict[str, Any]:
    """Execute a single automation action."""
    action_type = action.get("type", "noop")
    
    if action_type == "webhook":
        return _execute_webhook(document, action)
    elif action_type == "tag_document":
        return _execute_tag_document(db, document, action)
    elif action_type == "run_agent":
        return _execute_run_agent(db, document, action)
    elif action_type == "noop":
        return {"status": "success", "message": "No operation performed"}
    else:
        return {"status": "failed", "error": f"Unknown action type: {action_type}"}


def _execute_webhook(document: Document, action: dict[str, Any]) -> dict[str, Any]:
    url = action.get("url")
    if not url:
        return {"status": "failed", "error": "No URL provided for webhook"}

    payload = {
        "event": "document_processed",
        "document_id": str(document.id),
        "org_id": str(document.org_id),
        "confirmed_type": document.confirmed_type,
        "document_subtype": document.document_subtype,
        "extracted_data": document.extracted_data,
        "metadata": document.meta_data,
    }

    try:
        with httpx.Client() as client:
            response = client.post(
                url,
                json=payload,
                timeout=10.0,
                headers={"X-Nexiss-Event": "document_processed"}
            )
            response.raise_for_status()
            return {
                "status": "success",
                "http_status": response.status_code,
                "response": response.json() if response.content and "application/json" in response.headers.get("content-type", "") else response.text
            }
    except Exception as e:
        logger.error(f"Webhook failed: {e}")
        return {"status": "failed", "error": str(e)}


def _execute_tag_document(db: Session, document: Document, action: dict[str, Any]) -> dict[str, Any]:
    tags = action.get("tags", [])
    if not isinstance(tags, list):
        return {"status": "failed", "error": "Tags must be a list"}
    
    # Assuming Document model has a tags field in meta_data
    meta = document.meta_data or {}
    current_tags = meta.get("tags", [])
    if not isinstance(current_tags, list):
        current_tags = []
    
    new_tags = list(set(current_tags + tags))
    document.meta_data = {**meta, "tags": new_tags}
    return {"status": "success", "added_tags": tags}

def _execute_run_agent(db: Session, document: Document, action: dict[str, Any]) -> dict[str, Any]:
    agent_name = action.get("agent_name")
    if not agent_name:
        return {"status": "failed", "error": "No agent_name provided for run_agent action"}
    
    agent_func = AGENT_REGISTRY.get(agent_name)
    if not agent_func:
        return {"status": "failed", "error": f"Unknown agent: {agent_name}"}
    
    action_params = action.get("params", {})
    try:
        return agent_func(db, document, action_params)
    except Exception as e:
        logger.error(f"Agent {agent_name} failed: {e}")
        return {"status": "failed", "agent": agent_name, "error": str(e)}
