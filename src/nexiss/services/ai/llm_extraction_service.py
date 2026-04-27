from __future__ import annotations

import json
from decimal import Decimal

import httpx

from nexiss.core.config import get_settings
from nexiss.db.models.document import Document
from nexiss.services.ai.types import LLMExtractionResult

settings = get_settings()


class LLMExtractionService:
    def extract(self, document: Document, ocr_text: str) -> LLMExtractionResult:
        if settings.llm_provider == "mock":
            return self._mock_extract(document, ocr_text)
        if settings.llm_provider == "openai":
            return self._openai_extract(document, ocr_text)
        raise ValueError(f"Unsupported LLM provider: {settings.llm_provider}")

    @staticmethod
    def _mock_extract(document: Document, ocr_text: str) -> LLMExtractionResult:
        word_count = len([part for part in ocr_text.split(" ") if part.strip()])
        tokens_input = max(word_count, 1)
        tokens_output = max(tokens_input // 3, 1)
        data = {
            "document_type": "generic",
            "file_name": document.file_name,
            "content_type": document.content_type,
            "summary": f"Extracted with mock model from {tokens_input} input tokens.",
        }
        return LLMExtractionResult(
            extracted_data=data,
            confidence_score=Decimal("0.9000"),
            tokens_input=tokens_input,
            tokens_output=tokens_output,
        )

    @staticmethod
    def _openai_extract(document: Document, ocr_text: str) -> LLMExtractionResult:
        if not settings.openai_api_key:
            raise RuntimeError("OPENAI_API_KEY is not configured")

        prompt = (
            "Extract structured JSON from this OCR text.\n"
            "Return ONLY valid JSON.\n\n"
            f"File name: {document.file_name}\n"
            f"Content type: {document.content_type}\n\n"
            f"OCR:\n{ocr_text}\n"
        )

        url = f"{settings.openai_base_url.rstrip('/')}/responses"
        payload = {
            "model": settings.llm_model,
            "input": prompt,
            "text": {"format": {"type": "json_object"}},
        }
        headers = {"Authorization": f"Bearer {settings.openai_api_key}"}

        with httpx.Client(timeout=settings.llm_timeout_seconds) as client:
            resp = client.post(url, json=payload, headers=headers)
            resp.raise_for_status()
            body = resp.json()

        output_text = ""
        for item in body.get("output", []):
            for content in item.get("content", []):
                if content.get("type") == "output_text" and content.get("text"):
                    output_text += content["text"]
        extracted_data = json.loads(output_text) if output_text else {"raw": body}

        usage = body.get("usage") or {}
        tokens_input = int(usage.get("input_tokens") or 0)
        tokens_output = int(usage.get("output_tokens") or 0)

        return LLMExtractionResult(
            extracted_data=extracted_data,
            confidence_score=Decimal("0.8500"),
            tokens_input=max(tokens_input, 1),
            tokens_output=max(tokens_output, 1),
        )
