from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal


@dataclass(slots=True)
class OCRResult:
    text: str
    page_count: int


@dataclass(slots=True)
class LLMExtractionResult:
    extracted_data: dict
    confidence_score: Decimal
    tokens_input: int
    tokens_output: int
