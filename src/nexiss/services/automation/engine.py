from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.orm import Session

from nexiss.db.models.automation import (
    AutomationRule,
    AutomationRun,
    AutomationRunStatus,
    AutomationTriggerType,
)
from nexiss.db.models.document import Document


@dataclass(slots=True)
class AutomationExecutionResult:
    runs_created: int
    succeeded: int
    failed: int


def _rule_matches_document(rule: AutomationRule, document: Document) -> bool:
    allowed_types = rule.conditions.get("content_types")
    if isinstance(allowed_types, list) and allowed_types:
        return document.content_type in allowed_types
    return True


def _resolve_actions(rule: AutomationRule, document: Document) -> list[dict]:
    actions = rule.actions.get("steps", [])
    if not isinstance(actions, list):
        return []
    normalized: list[dict] = []
    for action in actions:
        if not isinstance(action, dict):
            continue
        normalized.append({"type": action.get("type", "noop"), "document_id": str(document.id)})
    return normalized


def execute_internal_automation(
    db: Session,
    *,
    document: Document,
    trigger_type: AutomationTriggerType,
) -> AutomationExecutionResult:
    rules = db.execute(
        select(AutomationRule).where(
            AutomationRule.org_id == document.org_id,
            AutomationRule.is_enabled.is_(True),
            AutomationRule.trigger_type == trigger_type,
        )
    ).scalars().all()

    runs_created = 0
    succeeded = 0
    failed = 0

    for rule in rules:
        if not _rule_matches_document(rule, document):
            continue

        executed_actions = _resolve_actions(rule, document)
        run_status = AutomationRunStatus.succeeded
        error_message = None
        if not executed_actions:
            run_status = AutomationRunStatus.failed
            error_message = "No valid actions resolved"

        db.add(
            AutomationRun(
                org_id=document.org_id,
                rule_id=rule.id,
                document_id=document.id,
                trigger_type=trigger_type,
                status=run_status,
                action_count=len(executed_actions),
                error_message=error_message,
                executed_actions={"actions": executed_actions} if executed_actions else None,
            )
        )
        runs_created += 1
        if run_status == AutomationRunStatus.succeeded:
            succeeded += 1
        else:
            failed += 1

    return AutomationExecutionResult(runs_created=runs_created, succeeded=succeeded, failed=failed)
