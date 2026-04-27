from __future__ import annotations

from types import SimpleNamespace

import pytest

from nexiss.services.ai import textract_service


def test_textract_requires_s3_bucket(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(textract_service.settings, "s3_bucket", "")
    service = textract_service.TextractOCRService()
    with pytest.raises(RuntimeError):
        service.extract(SimpleNamespace(storage_key="x", file_name="a", content_type="application/pdf"))

