from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from nexiss.db.models.automation import (
    AutomationRule,
    AutomationRun,
    AutomationRunStatus,
    AutomationTriggerType,
)
from nexiss.db.models.document import Document
from nexiss.services.automation.executor import execute_action


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

        actions = rule.actions.get("steps", [])
        if not isinstance(actions, list) or not actions:
            db.add(
                AutomationRun(
                    org_id=document.org_id,
                    rule_id=rule.id,
                    document_id=document.id,
                    trigger_type=trigger_type,
                    status=AutomationRunStatus.failed,
                    action_count=0,
                    error_message="No valid actions resolved",
                )
            )
            runs_created += 1
            failed += 1
            continue

        executed_results: list[dict[str, Any]] = []
        overall_status = AutomationRunStatus.succeeded
        error_message = None

        for action in actions:
            if not isinstance(action, dict):
                continue
            
            result = execute_action(db, rule, document, action)
            executed_results.append({"action": action, "result": result})
            
            if result.get("status") == "failed":
                overall_status = AutomationRunStatus.failed
                error_message = result.get("error")

        db.add(
            AutomationRun(
                org_id=document.org_id,
                rule_id=rule.id,
                document_id=document.id,
                trigger_type=trigger_type,
                status=overall_status,
                action_count=len(executed_results),
                error_message=error_message,
                executed_actions={"results": executed_results},
            )
        )
        runs_created += 1
        if overall_status == AutomationRunStatus.succeeded:
            succeeded += 1
        else:
            failed += 1

    return AutomationExecutionResult(runs_created=runs_created, succeeded=succeeded, failed=failed)
