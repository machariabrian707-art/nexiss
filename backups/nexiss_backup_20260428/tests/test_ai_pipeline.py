"""Tests for the AI document processing pipeline.

Covers OCR service, LLM extraction service, and the combined pipeline.
All tests run in mock mode (no external services required).
"""
from __future__ import annotations

from decimal import Decimal
from types import SimpleNamespace

import pytest

from nexiss.services.ai.llm_extraction_service import LLMExtractionService
from nexiss.services.ai.ocr_service import OCRService
from nexiss.services.ai.pipeline import DocumentProcessingPipeline


def _make_doc(
    file_name: str = "invoice.pdf",
    declared_type: str | None = None,
    confirmed_type: str | None = None,
):
    return SimpleNamespace(
        file_name=file_name,
        content_type="application/pdf",
        storage_key="org/raw/invoice.pdf",
        declared_type=declared_type,
        confirmed_type=confirmed_type,
    )


def test_ocr_service_mock_extract_returns_text_and_page_count() -> None:
    service = OCRService()
    document = _make_doc()
    result = service.extract_text(document)

    assert result.page_count == 1
    assert "invoice.pdf" in result.text


def test_llm_service_mock_extract_returns_tokens_and_confidence() -> None:
    service = LLMExtractionService()
    document = _make_doc()
    result = service.extract(document, "some ocr text content")

    assert isinstance(result.confidence_score, Decimal)
    assert result.tokens_input >= 1
    assert result.tokens_output >= 1
    assert result.extracted_data["file_name"] == "invoice.pdf"


def test_llm_mock_uses_declared_type_in_extraction() -> None:
    service = LLMExtractionService()
    document = _make_doc(declared_type="medical_healthcare")
    result = service.extract(document, "Patient: John")
    # Mock sets document_type from declared_type
    assert result.extracted_data["document_type"] == "medical_healthcare"


def test_llm_mock_falls_back_to_unknown_when_no_type() -> None:
    service = LLMExtractionService()
    document = _make_doc()
    result = service.extract(document, "some text")
    assert result.extracted_data["document_type"] == "unknown"


def test_llm_service_openai_requires_api_key(monkeypatch) -> None:
    monkeypatch.setattr("nexiss.services.ai.llm_extraction_service.settings.openai_api_key", None)
    monkeypatch.setattr("nexiss.services.ai.llm_extraction_service.settings.llm_provider", "openai")
    service = LLMExtractionService()
    document = _make_doc()
    with pytest.raises(RuntimeError):
        service.extract(document, "ocr text")


def test_document_pipeline_runs_all_steps() -> None:
    pipeline = DocumentProcessingPipeline()
    document = _make_doc(declared_type="business_financial")
    result = pipeline.run(document)

    assert result.page_count == 1
    assert result.tokens_input >= 1
    assert result.tokens_output >= 1
    # Classification step must produce a confirmed_type
    assert result.confirmed_type is not None
    assert result.document_subtype is not None
    # Entities list comes from classifier (empty in mock)
    assert isinstance(result.entities, list)


def test_document_pipeline_confirmed_type_matches_declared() -> None:
    """Mock classifier uses declared_type, so confirmed_type should match."""
    pipeline = DocumentProcessingPipeline()
    document = _make_doc(declared_type="medical_healthcare")
    result = pipeline.run(document)
    assert result.confirmed_type == "medical_healthcare"
