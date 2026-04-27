"""Tests for document classification service and DocumentCategory enum."""
from __future__ import annotations

from decimal import Decimal
from types import SimpleNamespace

import pytest

from nexiss.db.models.classification import (
    CATEGORY_LABELS,
    CATEGORY_SUBTYPES,
    DocumentCategory,
)
from nexiss.services.ai.classifier_service import DocumentClassifierService


def _make_doc(declared_type: str | None = None, file_name: str = "test.pdf"):
    return SimpleNamespace(
        file_name=file_name,
        declared_type=declared_type,
        content_type="application/pdf",
    )


def test_all_categories_have_labels():
    for cat in DocumentCategory:
        assert cat in CATEGORY_LABELS, f"Missing label for {cat}"


def test_all_categories_have_subtypes():
    for cat in DocumentCategory:
        assert cat in CATEGORY_SUBTYPES, f"Missing subtypes for {cat}"
        assert len(CATEGORY_SUBTYPES[cat]) >= 1


def test_mock_classifier_uses_declared_type():
    service = DocumentClassifierService()
    doc = _make_doc(declared_type="medical_healthcare")
    cat, subtype, confidence, entities = service.classify(doc, "Patient: John\nDiagnosis: flu")
    assert cat == "medical_healthcare"
    assert isinstance(confidence, Decimal)
    assert 0 < float(confidence) <= 1
    assert entities == []


def test_mock_classifier_defaults_to_other_on_unknown_type():
    service = DocumentClassifierService()
    doc = _make_doc(declared_type="not_a_real_category")
    cat, subtype, confidence, entities = service.classify(doc, "random text")
    assert cat == "other"


def test_mock_classifier_handles_no_declared_type():
    service = DocumentClassifierService()
    doc = _make_doc(declared_type=None)
    cat, subtype, confidence, entities = service.classify(doc, "")
    assert cat == "other"


def test_mock_classifier_returns_first_subtype_for_category():
    service = DocumentClassifierService()
    doc = _make_doc(declared_type="business_financial")
    cat, subtype, confidence, entities = service.classify(doc, "Invoice total: $500")
    assert cat == "business_financial"
    assert subtype == CATEGORY_SUBTYPES[DocumentCategory.business_financial][0]


def test_openai_classifier_raises_without_api_key(monkeypatch):
    monkeypatch.setattr(
        "nexiss.services.ai.classifier_service.settings.llm_provider", "openai"
    )
    monkeypatch.setattr(
        "nexiss.services.ai.classifier_service.settings.openai_api_key", None
    )
    service = DocumentClassifierService()
    doc = _make_doc(declared_type="legal")
    with pytest.raises(RuntimeError, match="OPENAI_API_KEY"):
        service.classify(doc, "Contract between parties")
