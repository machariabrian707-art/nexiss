"""Upgraded processing pipeline.

Step 1: OCR  — extract raw text from document file.
Step 2: LLM extraction  — produce structured JSON from the text.
Step 3: Classification  — confirm doc category + subtype.
Step 4: Entity extraction  — identify named entities from the extracted data.

All steps are synchronous (called from Celery worker) and return a single
DocumentPipelineResult that the task persists to the DB.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal

from nexiss.db.models.document import Document
from nexiss.services.ai.classifier_service import DocumentClassifierService
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
    document_subtype: str
    type_confidence: Decimal
    # List of {"name": str, "kind": str} from the classifier
    entities: list[dict] = field(default_factory=list)


class DocumentProcessingPipeline:
    def __init__(
        self,
        ocr_service: OCRService | None = None,
        llm_service: LLMExtractionService | None = None,
        classifier_service: DocumentClassifierService | None = None,
    ) -> None:
        self.ocr_service = ocr_service or OCRService()
        self.llm_service = llm_service or LLMExtractionService()
        self.classifier_service = classifier_service or DocumentClassifierService()

    def run(self, document: Document) -> DocumentPipelineResult:
        # Step 1: OCR
        ocr_result = self.ocr_service.extract_text(document)

        # Step 2: Structured extraction
        llm_result = self.llm_service.extract(document, ocr_result.text)

        # Step 3: Classification
        confirmed_type, subtype, type_confidence, entities = self.classifier_service.classify(
            document, ocr_result.text
        )

        return DocumentPipelineResult(
            page_count=ocr_result.page_count,
            extracted_data=llm_result.extracted_data,
            confidence_score=llm_result.confidence_score,
            tokens_input=llm_result.tokens_input,
            tokens_output=llm_result.tokens_output,
            confirmed_type=confirmed_type,
            document_subtype=subtype,
            type_confidence=type_confidence,
            entities=entities,
        )
