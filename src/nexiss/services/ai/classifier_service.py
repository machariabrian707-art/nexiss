"""Document classifier service.

Determines the DocumentCategory and sub-type of a processed document.
Uses two sources:
  1. declared_type — the category the user provided on upload (strong hint).
  2. extracted_data  — what the LLM pulled from the document text.

If LLM_PROVIDER=openai, we send an additional lightweight classification
call. If mock, we derive a best-guess from the declared_type or filename.

Returns (confirmed_type: str, subtype: str, confidence: Decimal).
"""
from __future__ import annotations

import json
from decimal import Decimal

import httpx

from nexiss.core.config import get_settings
from nexiss.db.models.classification import (
    CATEGORY_SUBTYPES,
    DocumentCategory,
)
from nexiss.db.models.document import Document

settings = get_settings()

_CLASSIFICATION_PROMPT = """
You are a document classifier for a Universal Document Intelligence platform.
Given the extracted text below, output ONLY a JSON object with:
  - "category": one of {categories}
  - "subtype": the most specific sub-type (use underscore_case)
  - "confidence": float 0.0-1.0
  - "entities": list of objects with "name" and "kind" (person/company/patient/vendor/other)

Declared type hint (may be empty): {declared_type}
File name: {file_name}
Extracted text (first 2000 chars): {ocr_text}
"""


class DocumentClassifierService:
    def classify(
        self,
        document: Document,
        extracted_text: str,
    ) -> tuple[str, str, Decimal, list[dict]]:
        """
        Returns (confirmed_category, subtype, confidence, entities_list).
        entities_list items: {"name": str, "kind": str}
        """
        if settings.llm_provider == "openai":
            return self._openai_classify(document, extracted_text)
        return self._mock_classify(document)

    @staticmethod
    def _mock_classify(
        document: Document,
    ) -> tuple[str, str, Decimal, list[dict]]:
        """Derive category from declared_type or fall back to 'other'."""
        declared = document.declared_type or ""
        try:
            cat = DocumentCategory(declared)
        except ValueError:
            cat = DocumentCategory.other

        subtypes = CATEGORY_SUBTYPES.get(cat, ["unknown"])
        subtype = subtypes[0] if subtypes else "unknown"
        return cat.value, subtype, Decimal("0.7500"), []

    @staticmethod
    def _openai_classify(
        document: Document,
        extracted_text: str,
    ) -> tuple[str, str, Decimal, list[dict]]:
        if not settings.openai_api_key:
            raise RuntimeError("OPENAI_API_KEY is not configured")

        categories = ", ".join(c.value for c in DocumentCategory)
        prompt = _CLASSIFICATION_PROMPT.format(
            categories=categories,
            declared_type=document.declared_type or "",
            file_name=document.file_name,
            ocr_text=extracted_text[:2000],
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
                if content.get("type") == "output_text":
                    output_text += content.get("text", "")

        result = json.loads(output_text) if output_text else {}

        raw_cat = result.get("category", "other")
        try:
            cat = DocumentCategory(raw_cat)
        except ValueError:
            cat = DocumentCategory.other

        subtype = result.get("subtype", "unknown")
        confidence = Decimal(str(min(max(float(result.get("confidence", 0.75)), 0.0), 1.0)))
        entities = result.get("entities", [])

        return cat.value, subtype, confidence, entities
