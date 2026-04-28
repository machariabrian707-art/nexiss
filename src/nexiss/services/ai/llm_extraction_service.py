"""LLM extraction service — document-type-aware prompt builder.

Fixed: _openai_classify now uses DocumentCategory (the 12 super-categories)
instead of the old flat DocumentType enum, keeping both systems in sync.
"""
from __future__ import annotations

import json
from decimal import Decimal

import httpx

from nexiss.core.config import get_settings
from nexiss.db.models.classification import DocumentCategory
from nexiss.db.models.document import Document
from nexiss.services.ai.types import LLMExtractionResult

settings = get_settings()

_BASE_PROMPT = """\
You are Nexiss, a document intelligence system.
Extract structured data from the OCR text below and return ONLY valid JSON — no markdown, no commentary.

File name: {file_name}
Content type: {content_type}
Document type: {doc_type}
"""

_TYPE_INSTRUCTIONS: dict[str, str] = {
    "invoice": "Extract: vendor_name, vendor_address, invoice_number, invoice_date, due_date, line_items (array of {description, quantity, unit_price, total}), subtotal, tax, total_amount, currency, payment_terms.",
    "receipt": "Extract: vendor_name, date, items (array of {name, price}), subtotal, tax, total_amount, currency, payment_method.",
    "patient_record": "Extract: patient_name, patient_id, date_of_birth, visit_date, doctor_name, facility, diagnosis (array), medications (array of {name, dose, frequency}), lab_values (object), notes.",
    "prescription": "Extract: patient_name, doctor_name, date, medications (array of {name, dose, frequency, duration}), notes.",
    "lab_result": "Extract: patient_name, patient_id, doctor_name, facility, date, tests (array of {test_name, value, unit, reference_range, flag}), notes.",
    "contract": "Extract: document_title, parties (array), effective_date, expiry_date, jurisdiction, key_clauses (array of short summaries), obligations (array), risk_flags (array).",
    "agreement": "Extract: document_title, parties (array), effective_date, expiry_date, jurisdiction, key_clauses (array of short summaries), obligations (array), risk_flags (array).",
    "cv_resume": "Extract: full_name, email, phone, address, skills (array), work_experience (array of {company, role, start_date, end_date, description}), education (array of {institution, degree, year}), certifications (array).",
    "employee_record": "Extract: employee_name, employee_id, job_title, department, hire_date, salary, currency, skills (array), notes.",
    "national_id": "Extract: full_name, document_number, nationality, date_of_birth, issue_date, expiry_date, issuing_authority.",
    "passport": "Extract: full_name, document_number, nationality, date_of_birth, issue_date, expiry_date, issuing_authority.",
    "bill_of_lading": "Extract: shipper, consignee, tracking_number, origin, destination, ship_date, estimated_delivery, items (array of {description, quantity, weight}), total_weight, total_value.",
    "bank_statement": "Extract: account_holder, account_number, bank_name, statement_period_start, statement_period_end, opening_balance, closing_balance, transactions (array of {date, description, debit, credit, balance}).",
}

_DEFAULT_INSTRUCTION = "Extract all key fields, dates, names, amounts, and identifiers as a structured JSON object."

_CLASSIFICATION_PROMPT = """\
You are Nexiss, a document intelligence system.
Given the OCR text below, determine the document category.

Respond ONLY with valid JSON in this format:
{{"category": "<category>", "confidence": <0.0-1.0>}}

Valid categories: {valid_categories}

OCR TEXT:
{ocr_text}
"""


def _build_prompt(document: Document, ocr_text: str, doc_type: str) -> str:
    instruction = _TYPE_INSTRUCTIONS.get(doc_type, _DEFAULT_INSTRUCTION)
    return (
        _BASE_PROMPT.format(
            file_name=document.file_name,
            content_type=document.content_type,
            doc_type=doc_type,
        )
        + "\n"
        + instruction
        + "\n\nOCR TEXT:\n"
        + ocr_text
    )


class LLMExtractionService:
    def extract(self, document: Document, ocr_text: str) -> LLMExtractionResult:
        if settings.llm_provider == "mock":
            return self._mock_extract(document, ocr_text)
        if settings.llm_provider == "openai":
            return self._openai_extract(document, ocr_text)
        raise ValueError(f"Unsupported LLM provider: {settings.llm_provider}")

    # ------------------------------------------------------------------
    # Mock
    # ------------------------------------------------------------------
    @staticmethod
    def _mock_extract(document: Document, ocr_text: str) -> LLMExtractionResult:
        word_count = len([p for p in ocr_text.split(" ") if p.strip()])
        tokens_input = max(word_count, 1)
        tokens_output = max(tokens_input // 3, 1)
        doc_type = getattr(document, "declared_type", None) or "unknown"
        data = {
            "document_type": doc_type,
            "file_name": document.file_name,
            "content_type": document.content_type,
            "summary": f"Mock extraction for type '{doc_type}' from {tokens_input} tokens.",
        }
        return LLMExtractionResult(
            extracted_data=data,
            confidence_score=Decimal("0.9000"),
            tokens_input=tokens_input,
            tokens_output=tokens_output,
        )

    # ------------------------------------------------------------------
    # OpenAI
    # ------------------------------------------------------------------
    def _openai_extract(self, document: Document, ocr_text: str) -> LLMExtractionResult:
        if not settings.openai_api_key:
            raise RuntimeError("OPENAI_API_KEY is not configured")

        doc_type = (
            getattr(document, "declared_type", None)
            or getattr(document, "confirmed_type", None)
            or "unknown"
        )
        prompt = _build_prompt(document, ocr_text, doc_type)
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
