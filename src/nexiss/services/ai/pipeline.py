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


class DocumentProcessingPipeline:
    def __init__(
        self,
        ocr_service: OCRService | None = None,
        llm_service: LLMExtractionService | None = None,
    ) -> None:
        self.ocr_service = ocr_service or OCRService()
        self.llm_service = llm_service or LLMExtractionService()

    def run(self, document: Document) -> DocumentPipelineResult:
        ocr_result = self.ocr_service.extract_text(document)
        llm_result = self.llm_service.extract(document, ocr_result.text)
        return DocumentPipelineResult(
            page_count=ocr_result.page_count,
            extracted_data=llm_result.extracted_data,
            confidence_score=llm_result.confidence_score,
            tokens_input=llm_result.tokens_input,
            tokens_output=llm_result.tokens_output,
        )
