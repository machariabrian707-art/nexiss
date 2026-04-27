from __future__ import annotations

import time
from dataclasses import dataclass

from nexiss.core.config import get_settings
from nexiss.db.models.document import Document
from nexiss.services.ai.types import OCRResult

settings = get_settings()


@dataclass(slots=True)
class TextractConfig:
    bucket: str
    poll_interval_seconds: int
    max_wait_seconds: int


def _config() -> TextractConfig:
    if not settings.s3_bucket:
        raise RuntimeError("S3_BUCKET is not configured")
    return TextractConfig(
        bucket=settings.s3_bucket,
        poll_interval_seconds=settings.textract_poll_interval_seconds,
        max_wait_seconds=settings.textract_max_wait_seconds,
    )


def _get_textract_client():
    try:
        import boto3  # type: ignore
    except ModuleNotFoundError as exc:
        raise RuntimeError("boto3 is required for aws_textract OCR") from exc
    return boto3.client("textract", region_name=settings.s3_region)


def _extract_lines_from_blocks(blocks: list[dict]) -> list[str]:
    lines: list[str] = []
    for block in blocks:
        if block.get("BlockType") == "LINE" and block.get("Text"):
            lines.append(block["Text"])
    return lines


class TextractOCRService:
    def extract(self, document: Document) -> OCRResult:
        cfg = _config()
        client = _get_textract_client()

        # Textract async path works for PDFs stored in S3.
        start = client.start_document_text_detection(
            DocumentLocation={"S3Object": {"Bucket": cfg.bucket, "Name": document.storage_key}}
        )
        job_id = start["JobId"]

        deadline = time.time() + cfg.max_wait_seconds
        next_token = None
        all_blocks: list[dict] = []

        while True:
            if time.time() > deadline:
                raise TimeoutError("Textract job timed out")

            kwargs = {"JobId": job_id}
            if next_token:
                kwargs["NextToken"] = next_token

            resp = client.get_document_text_detection(**kwargs)
            status = resp.get("JobStatus")

            if status in {"IN_PROGRESS"}:
                time.sleep(cfg.poll_interval_seconds)
                continue
            if status in {"FAILED", "PARTIAL_SUCCESS"}:
                raise RuntimeError(f"Textract failed with status={status}")

            all_blocks.extend(resp.get("Blocks") or [])
            next_token = resp.get("NextToken")
            if not next_token:
                break

        lines = _extract_lines_from_blocks(all_blocks)
        text = "\n".join(lines).strip()
        page_count = max(1, len({b.get("Page") for b in all_blocks if b.get("Page")}))
        return OCRResult(text=text, page_count=page_count)
