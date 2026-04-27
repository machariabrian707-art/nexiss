from __future__ import annotations

from decimal import Decimal
from types import SimpleNamespace

import pytest

from nexiss.services.ai.llm_extraction_service import LLMExtractionService
from nexiss.services.ai.ocr_service import OCRService
from nexiss.services.ai.pipeline import DocumentProcessingPipeline


def test_ocr_service_mock_extract_returns_text_and_page_count() -> None:
    service = OCRService()
    document = SimpleNamespace(
        file_name="invoice.pdf",
        content_type="application/pdf",
        storage_key="org/raw/invoice.pdf",
    )
    result = service.extract_text(document)

    assert result.page_count == 1
    assert "invoice.pdf" in result.text


def test_llm_service_mock_extract_returns_tokens_and_confidence() -> None:
    service = LLMExtractionService()
    document = SimpleNamespace(file_name="invoice.pdf", content_type="application/pdf")
    result = service.extract(document, "some ocr text content")

    assert isinstance(result.confidence_score, Decimal)
    assert result.tokens_input >= 1
    assert result.tokens_output >= 1
    assert result.extracted_data["file_name"] == "invoice.pdf"


def test_llm_service_openai_requires_api_key(monkeypatch) -> None:
    monkeypatch.setattr("nexiss.services.ai.llm_extraction_service.settings.openai_api_key", None)
    monkeypatch.setattr("nexiss.services.ai.llm_extraction_service.settings.llm_provider", "openai")
    service = LLMExtractionService()
    document = SimpleNamespace(file_name="invoice.pdf", content_type="application/pdf")
    with pytest.raises(RuntimeError):
        service.extract(document, "ocr text")


def test_document_pipeline_combines_ocr_and_llm_outputs() -> None:
    pipeline = DocumentProcessingPipeline()
    document = SimpleNamespace(
        file_name="invoice.pdf",
        content_type="application/pdf",
        storage_key="org/raw/invoice.pdf",
    )
    result = pipeline.run(document)

    assert result.page_count == 1
    assert result.tokens_input >= 1
    assert result.tokens_output >= 1
    assert result.extracted_data["document_type"] == "generic"
