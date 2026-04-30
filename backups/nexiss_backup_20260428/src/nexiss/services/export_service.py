"""Export service: convert a list of documents + their extracted_data into CSV or XLSX.

This is a core Nexiss feature — turning messy scanned docs into clean spreadsheets.
"""
from __future__ import annotations

import csv
import io
from typing import Literal

from nexiss.db.models.document import Document


def _flatten(extracted_data: dict | None, prefix: str = "") -> dict:
    """Flatten a nested dict one level deep for spreadsheet columns."""
    if not extracted_data:
        return {}
    flat: dict = {}
    for k, v in extracted_data.items():
        col = f"{prefix}{k}" if prefix else k
        if isinstance(v, dict):
            for kk, vv in v.items():
                flat[f"{col}.{kk}"] = vv
        elif isinstance(v, list):
            flat[col] = "; ".join(str(i) for i in v) if v else ""
        else:
            flat[col] = v
    return flat


def _doc_to_row(doc: Document) -> dict:
    base = {
        "id": str(doc.id),
        "file_name": doc.file_name,
        "declared_type": doc.declared_type or "",
        "confirmed_type": doc.confirmed_type or "",
        "type_confidence": str(doc.type_confidence or ""),
        "status": doc.status.value,
        "page_count": doc.page_count or "",
        "confidence_score": str(doc.confidence_score or ""),
        "created_at": doc.created_at.isoformat(),
    }
    extracted = _flatten(doc.extracted_data)
    return {**base, **extracted}


def export_csv(documents: list[Document]) -> bytes:
    """Return UTF-8 CSV bytes for a list of documents."""
    if not documents:
        return b""

    rows = [_doc_to_row(d) for d in documents]
    # Collect all column names across all rows
    all_keys: list[str] = []
    seen: set[str] = set()
    for row in rows:
        for k in row:
            if k not in seen:
                all_keys.append(k)
                seen.add(k)

    buf = io.StringIO()
    writer = csv.DictWriter(buf, fieldnames=all_keys, extrasaction="ignore")
    writer.writeheader()
    for row in rows:
        writer.writerow(row)
    return buf.getvalue().encode("utf-8")


def export_xlsx(documents: list[Document]) -> bytes:
    """Return XLSX bytes for a list of documents.

    Uses openpyxl if available; falls back to CSV if not installed.
    openpyxl is listed as an optional dependency in pyproject.toml.
    """
    try:
        import openpyxl  # type: ignore
    except ImportError:
        # Graceful fallback — return CSV bytes with a .csv-compatible format
        return export_csv(documents)

    if not documents:
        return b""

    rows = [_doc_to_row(d) for d in documents]
    all_keys: list[str] = []
    seen: set[str] = set()
    for row in rows:
        for k in row:
            if k not in seen:
                all_keys.append(k)
                seen.add(k)

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Nexiss Export"
    ws.append(all_keys)
    for row in rows:
        ws.append([row.get(k, "") for k in all_keys])

    buf = io.BytesIO()
    wb.save(buf)
    return buf.getvalue()
