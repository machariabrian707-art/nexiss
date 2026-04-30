from __future__ import annotations

from nexiss.core.config import get_settings
from nexiss.db.models.document import Document
from nexiss.services.ai.textract_service import TextractOCRService
from nexiss.services.ai.openai_ocr_service import OpenAIOCRService
from nexiss.services.ai.types import OCRResult

settings = get_settings()


class OCRService:
    def extract_text(self, document: Document) -> OCRResult:
        if settings.ocr_provider == "mock":
            return self._mock_extract(document)
        if settings.ocr_provider == "aws_textract":
            return TextractOCRService().extract(document)
        if settings.ocr_provider == "openai":
            return OpenAIOCRService().extract(document)
        raise ValueError(f"Unsupported OCR provider: {settings.ocr_provider}")

    @staticmethod
    def _mock_extract(document: Document) -> OCRResult:
        body = (
            f"Document: {document.file_name}\n"
            f"Content-Type: {document.content_type}\n"
            f"Storage-Key: {document.storage_key}\n"
            "OCR provider: mock"
        )
        return OCRResult(text=body, page_count=1)

    # Textract provider is implemented in `services/ai/textract_service.py`.
