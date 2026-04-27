"""Document processing pipeline.

Flow:
  1. OCR  -> extract raw text
  2. Classify -> confirm document type (if not declared by user)
  3. Extract -> structured fields based on confirmed type
"""
from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from nexiss.db.models.document import Document
from nexiss.services.ai.llm_extraction_service import LLMExtractionService
from nexiss.services.ai.ocr_service import OCRService


@dataclass(slots=True)
class DocumentPipelineResult:
    page_count: int
    extracted_data: dict
    confidence_score: Decimal
    tokens_input: int
    tokens_output: int
    confirmed_type: str
    type_confidence: float


class DocumentProcessingPipeline:
    def __init__(
        self,
        ocr_service: OCRService | None = None,
        llm_service: LLMExtractionService | None = None,
    ) -> None:
        self.ocr_service = ocr_service or OCRService()
        self.llm_service = llm_service or LLMExtractionService()

    def run(self, document: Document) -> DocumentPipelineResult:
        # Step 1: OCR
        ocr_result = self.ocr_service.extract_text(document)

        # Step 2: Classify (skip if user already told us the type)
        if document.declared_type and document.declared_type != "unknown":
            confirmed_type = document.declared_type
            type_confidence = 1.0  # user declared it — we trust them
        else:
            confirmed_type, type_confidence = self.llm_service.classify(ocr_result.text)

        # Temporarily set confirmed_type on the document object so the
        # extraction prompt can use the right schema
        document.confirmed_type = confirmed_type  # type: ignore[assignment]

        # Step 3: Extract structured data
        llm_result = self.llm_service.extract(document, ocr_result.text)

        return DocumentPipelineResult(
            page_count=ocr_result.page_count,
            extracted_data=llm_result.extracted_data,
            confidence_score=llm_result.confidence_score,
            tokens_input=llm_result.tokens_input,
            tokens_output=llm_result.tokens_output,
            confirmed_type=confirmed_type,
            type_confidence=type_confidence,
        )
