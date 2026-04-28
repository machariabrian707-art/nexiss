from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import MagicMock
from uuid import uuid4

import httpx
import pytest
from sqlalchemy.orm import Session

from nexiss.db.models.automation import AutomationRun, AutomationTriggerType
from nexiss.db.models.billing import BillingSubscription, BillingSubscriptionStatus
from nexiss.services.automation.engine import execute_internal_automation


class FakeScalarResult:
    def __init__(self, rows):
        self._rows = rows

    def all(self):
        return self._rows

    def scalar_one_or_none(self):
        return self._rows[0] if self._rows else None


class FakeExecuteResult:
    def __init__(self, rows):
        self._rows = rows

    def scalars(self):
        return FakeScalarResult(self._rows)


class FakeSession:
    def __init__(self, rules=None, subscriptions=None):
        self.added = []
        self._rules = rules if rules is not None else []
        self._subscriptions = subscriptions if subscriptions is not None else []

    def execute(self, stmt):
        if "automation_rules" in str(stmt):
            return FakeExecuteResult(self._rules)
        if "billing_subscriptions" in str(stmt):
            return FakeExecuteResult(self._subscriptions)
        return FakeExecuteResult([])

    def add(self, value):
        self.added.append(value)


@pytest.fixture
def mock_db_session():
    return FakeSession()


@pytest.fixture
def mock_document():
    return SimpleNamespace(
        id=uuid4(),
        org_id=uuid4(),
        content_type="application/pdf",
        confirmed_type="invoice",
        document_subtype="utility",
        extracted_data={"invoice_number": "123"},
        meta_data={},
        type_confidence=0.95,
    )


def test_execute_internal_automation_creates_run_for_matching_rule(mock_db_session, mock_document) -> None:
    rule = SimpleNamespace(
        id=uuid4(),
        org_id=mock_document.org_id,
        is_enabled=True,
        trigger_type=AutomationTriggerType.document_processed,
        conditions={"content_types": ["application/pdf"]},
        actions={"steps": [{"type": "tag_document", "tags": ["test-tag"]}]},
    )
    mock_db_session._rules = [rule]

    result = execute_internal_automation(
        mock_db_session,
        document=mock_document,
        trigger_type=AutomationTriggerType.document_processed,
    )

    assert result.runs_created == 1
    assert result.succeeded == 1
    assert result.failed == 0
    assert len(mock_db_session.added) == 1
    assert mock_document.meta_data == {"tags": ["test-tag"]}
    assert isinstance(mock_db_session.added[0], AutomationRun)
    assert mock_db_session.added[0].status.value == "succeeded"


def test_execute_internal_automation_skips_non_matching_rule(mock_db_session, mock_document) -> None:
    rule = SimpleNamespace(
        id=uuid4(),
        org_id=mock_document.org_id,
        is_enabled=True,
        trigger_type=AutomationTriggerType.document_processed,
        conditions={"content_types": ["image/png"]},
        actions={"steps": [{"type": "tag_document"}]},
    )
    mock_db_session._rules = [rule]

    result = execute_internal_automation(
        mock_db_session,
        document=mock_document,
        trigger_type=AutomationTriggerType.document_processed,
    )

    assert result.runs_created == 0
    assert result.succeeded == 0
    assert result.failed == 0
    assert mock_db_session.added == []
    assert mock_document.meta_data == {}


def test_execute_internal_automation_webhook_action_succeeds(mock_db_session, mock_document, monkeypatch) -> None:
    webhook_url = "https://example.com/webhook"
    rule = SimpleNamespace(
        id=uuid4(),
        org_id=mock_document.org_id,
        is_enabled=True,
        trigger_type=AutomationTriggerType.document_processed,
        conditions={},
        actions={"steps": [{"type": "webhook", "url": webhook_url}]},
    )
    mock_db_session._rules = [rule]

    mock_post = MagicMock(return_value=SimpleNamespace(status_code=200, content=b'{}', json=lambda: {}))
    monkeypatch.setattr(httpx.Client, "post", mock_post)

    result = execute_internal_automation(
        mock_db_session,
        document=mock_document,
        trigger_type=AutomationTriggerType.document_processed,
    )

    assert result.runs_created == 1
    assert result.succeeded == 1
    assert result.failed == 0
    assert mock_post.called
    assert mock_post.call_args[0][0] == webhook_url
    assert mock_db_session.added[0].status.value == "succeeded"


def test_execute_internal_automation_webhook_action_fails(mock_db_session, mock_document, monkeypatch) -> None:
    webhook_url = "https://example.com/webhook"
    rule = SimpleNamespace(
        id=uuid4(),
        org_id=mock_document.org_id,
        is_enabled=True,
        trigger_type=AutomationTriggerType.document_processed,
        conditions={},
        actions={"steps": [{"type": "webhook", "url": webhook_url}]},
    )
    mock_db_session._rules = [rule]

    mock_post = MagicMock(side_effect=httpx.RequestError("Connection error", request=httpx.Request("POST", webhook_url)))
    monkeypatch.setattr(httpx.Client, "post", mock_post)

    result = execute_internal_automation(
        mock_db_session,
        document=mock_document,
        trigger_type=AutomationTriggerType.document_processed,
    )

    assert result.runs_created == 1
    assert result.succeeded == 0
    assert result.failed == 1
    assert mock_post.called
    assert mock_db_session.added[0].status.value == "failed"
    assert "Connection error" in mock_db_session.added[0].error_message


def test_execute_internal_automation_run_agent_payment_succeeds(mock_db_session, mock_document) -> None:
    rule = SimpleNamespace(
        id=uuid4(),
        org_id=mock_document.org_id,
        is_enabled=True,
        trigger_type=AutomationTriggerType.document_processed,
        conditions={},
        actions={"steps": [{"type": "run_agent", "agent_name": "payment_agent"}]},
    )
    mock_db_session._rules = [rule]

    # Mock an active subscription
    mock_db_session._subscriptions = [
        SimpleNamespace(
            org_id=mock_document.org_id,
            status=BillingSubscriptionStatus.active,
        )
    ]

    result = execute_internal_automation(
        mock_db_session,
        document=mock_document,
        trigger_type=AutomationTriggerType.document_processed,
    )

    assert result.runs_created == 1
    assert result.succeeded == 1
    assert result.failed == 0
    assert mock_db_session.added[0].status.value == "succeeded"


def test_execute_internal_automation_run_agent_payment_fails(mock_db_session, mock_document) -> None:
    rule = SimpleNamespace(
        id=uuid4(),
        org_id=mock_document.org_id,
        is_enabled=True,
        trigger_type=AutomationTriggerType.document_processed,
        conditions={},
        actions={"steps": [{"type": "run_agent", "agent_name": "payment_agent"}]},
    )
    mock_db_session._rules = [rule]

    # No active subscription mocked
    mock_db_session._subscriptions = []

    result = execute_internal_automation(
        mock_db_session,
        document=mock_document,
        trigger_type=AutomationTriggerType.document_processed,
    )

    assert result.runs_created == 1
    assert result.succeeded == 0
    assert result.failed == 1
    assert mock_db_session.added[0].status.value == "failed"
    assert "No active subscription found" in mock_db_session.added[0].error_message


def test_execute_internal_automation_run_agent_verification_flags_for_review(mock_db_session, mock_document) -> None:
    mock_document.type_confidence = 0.5
    rule = SimpleNamespace(
        id=uuid4(),
        org_id=mock_document.org_id,
        is_enabled=True,
        trigger_type=AutomationTriggerType.document_processed,
        conditions={},
        actions={"steps": [{"type": "run_agent", "agent_name": "verification_agent", "params": {"threshold": 0.7}}]},
    )
    mock_db_session._rules = [rule]

    result = execute_internal_automation(
        mock_db_session,
        document=mock_document,
        trigger_type=AutomationTriggerType.document_processed,
    )

    assert result.runs_created == 1
    assert result.succeeded == 1
    assert result.failed == 0
    assert mock_db_session.added[0].status.value == "succeeded"
    assert mock_document.meta_data.get("needs_manual_review") is True
    assert "Low confidence" in mock_document.meta_data.get("review_reason")


def test_execute_internal_automation_run_agent_extraction_fails_missing_fields(mock_db_session, mock_document) -> None:
    mock_document.extracted_data = {"field1": "value1"}
    rule = SimpleNamespace(
        id=uuid4(),
        org_id=mock_document.org_id,
        is_enabled=True,
        trigger_type=AutomationTriggerType.document_processed,
        conditions={},
        actions={"steps": [{"type": "run_agent", "agent_name": "extraction_agent", "params": {"required_fields": ["field1", "field2"]}}]},
    )
    mock_db_session._rules = [rule]

    result = execute_internal_automation(
        mock_db_session,
        document=mock_document,
        trigger_type=AutomationTriggerType.document_processed,
    )

    assert result.runs_created == 1
    assert result.succeeded == 0
    assert result.failed == 1
    assert mock_db_session.added[0].status.value == "failed"
    assert "Missing required fields: field2" in mock_db_session.added[0].executed_actions["results"][0]["result"]["error"]


def test_execute_internal_automation_multiple_actions_mixed_status(mock_db_session, mock_document, monkeypatch) -> None:
    webhook_url = "https://example.com/webhook"
    rule = SimpleNamespace(
        id=uuid4(),
        org_id=mock_document.org_id,
        is_enabled=True,
        trigger_type=AutomationTriggerType.document_processed,
        conditions={},
        actions={
            "steps": [
                {"type": "tag_document", "tags": ["first-tag"]},
                {"type": "webhook", "url": webhook_url}, # This will succeed
                {"type": "run_agent", "agent_name": "payment_agent"}, # This will fail due to no subscription
                {"type": "tag_document", "tags": ["last-tag"]},
            ]
        },
    )
    mock_db_session._rules = [rule]

    mock_post = MagicMock(return_value=SimpleNamespace(status_code=200, content=b'{}', json=lambda: {}))
    monkeypatch.setattr(httpx.Client, "post", mock_post)
    
    # No active subscription mocked for payment_agent to fail
    mock_db_session._subscriptions = []

    result = execute_internal_automation(
        mock_db_session,
        document=mock_document,
        trigger_type=AutomationTriggerType.document_processed,
    )

    assert result.runs_created == 1
    assert result.succeeded == 0  # Overall failed due to payment_agent
    assert result.failed == 1
    assert mock_document.meta_data.get("tags") == ["first-tag", "last-tag"] # Tags should still be applied
    assert mock_db_session.added[0].status.value == "failed"
    assert "No active subscription found" in mock_db_session.added[0].error_message
    assert len(mock_db_session.added[0].executed_actions["results"]) == 4
    # Check individual action results
    assert mock_db_session.added[0].executed_actions["results"][0]["result"]["status"] == "success"
    assert mock_db_session.added[0].executed_actions["results"][1]["result"]["status"] == "success"
    assert mock_db_session.added[0].executed_actions["results"][2]["result"]["status"] == "failed"
    assert mock_db_session.added[0].executed_actions["results"][3]["result"]["status"] == "success"


def test_execute_internal_automation_empty_actions_list(mock_db_session, mock_document) -> None:
    rule = SimpleNamespace(
        id=uuid4(),
        org_id=mock_document.org_id,
        is_enabled=True,
        trigger_type=AutomationTriggerType.document_processed,
        conditions={},
        actions={"steps": []},
    )
    mock_db_session._rules = [rule]

    result = execute_internal_automation(
        mock_db_session,
        document=mock_document,
        trigger_type=AutomationTriggerType.document_processed,
    )

    assert result.runs_created == 1
    assert result.succeeded == 0
    assert result.failed == 1
    assert mock_db_session.added[0].status.value == "failed"
    assert "No valid actions resolved" in mock_db_session.added[0].error_message



def test_execute_internal_automation_unknown_agent_fails(mock_db_session, mock_document) -> None:
    rule = SimpleNamespace(
        id=uuid4(),
        org_id=mock_document.org_id,
        is_enabled=True,
        trigger_type=AutomationTriggerType.document_processed,
        conditions={},
        actions={"steps": [{"type": "run_agent", "agent_name": "non_existent_agent"}]},
    )
    mock_db_session._rules = [rule]

    result = execute_internal_automation(
        mock_db_session,
        document=mock_document,
        trigger_type=AutomationTriggerType.document_processed,
    )

    assert result.runs_created == 1
    assert result.succeeded == 0
    assert result.failed == 1
    assert mock_db_session.added[0].status.value == "failed"
    assert "Unknown agent: non_existent_agent" in mock_db_session.added[0].error_message
