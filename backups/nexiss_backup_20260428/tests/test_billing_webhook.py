from __future__ import annotations

import pytest

from nexiss.services.billing import stripe_service


def test_require_webhook_secret_raises_if_missing(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(stripe_service.settings, "stripe_webhook_secret", None)
    with pytest.raises(ValueError):
        stripe_service.verify_and_construct_event(payload=b"{}", signature_header="t=1,v1=x")
