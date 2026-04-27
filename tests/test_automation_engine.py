from __future__ import annotations

from types import SimpleNamespace
from uuid import uuid4

from nexiss.db.models.automation import AutomationTriggerType
from nexiss.services.automation.engine import execute_internal_automation


def test_execute_internal_automation_creates_run_for_matching_rule() -> None:
    org_id = uuid4()
    rule = SimpleNamespace(
        id=uuid4(),
        org_id=org_id,
        is_enabled=True,
        trigger_type=AutomationTriggerType.document_processed,
        conditions={"content_types": ["application/pdf"]},
        actions={"steps": [{"type": "tag_document"}]},
    )
    document = SimpleNamespace(id=uuid4(), org_id=org_id, content_type="application/pdf")

    class FakeScalarResult:
        def __init__(self, rows):
            self._rows = rows

        def all(self):
            return self._rows

    class FakeExecuteResult:
        def __init__(self, rows):
            self._rows = rows

        def scalars(self):
            return FakeScalarResult(self._rows)

    class FakeSession:
        def __init__(self):
            self.added = []

        def execute(self, _stmt):
            return FakeExecuteResult([rule])

        def add(self, value):
            self.added.append(value)

    db = FakeSession()
    result = execute_internal_automation(
        db,
        document=document,
        trigger_type=AutomationTriggerType.document_processed,
    )

    assert result.runs_created == 1
    assert result.succeeded == 1
    assert result.failed == 0
    assert len(db.added) == 1


def test_execute_internal_automation_skips_non_matching_rule() -> None:
    org_id = uuid4()
    rule = SimpleNamespace(
        id=uuid4(),
        org_id=org_id,
        is_enabled=True,
        trigger_type=AutomationTriggerType.document_processed,
        conditions={"content_types": ["image/png"]},
        actions={"steps": [{"type": "tag_document"}]},
    )
    document = SimpleNamespace(id=uuid4(), org_id=org_id, content_type="application/pdf")

    class FakeScalarResult:
        def __init__(self, rows):
            self._rows = rows

        def all(self):
            return self._rows

    class FakeExecuteResult:
        def __init__(self, rows):
            self._rows = rows

        def scalars(self):
            return FakeScalarResult(self._rows)

    class FakeSession:
        def __init__(self):
            self.added = []

        def execute(self, _stmt):
            return FakeExecuteResult([rule])

        def add(self, value):
            self.added.append(value)

    db = FakeSession()
    result = execute_internal_automation(
        db,
        document=document,
        trigger_type=AutomationTriggerType.document_processed,
    )

    assert result.runs_created == 0
    assert result.succeeded == 0
    assert result.failed == 0
    assert db.added == []
