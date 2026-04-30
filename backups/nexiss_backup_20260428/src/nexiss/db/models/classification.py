"""Document classification types and the DocumentType enum used across Nexiss.

The 12 categories map directly to the product vision: every document uploaded
gets a declared_type (user hint) and a confirmed_type (AI verdict).
"""
from __future__ import annotations

import enum


class DocumentCategory(str, enum.Enum):
    """The 12 document super-categories supported by Nexiss."""

    # 1
    business_financial = "business_financial"
    # 2
    medical_healthcare = "medical_healthcare"
    # 3
    legal = "legal"
    # 4
    educational = "educational"
    # 5
    administrative_hr = "administrative_hr"
    # 6
    logistics_supply_chain = "logistics_supply_chain"
    # 7
    government_identity = "government_identity"
    # 8
    media_content = "media_content"
    # 9
    technical_data = "technical_data"
    # 10
    image_based = "image_based"
    # 11
    communication = "communication"
    # 12
    other = "other"


# Human-readable labels for each category (used in UI / analytics)
CATEGORY_LABELS: dict[DocumentCategory, str] = {
    DocumentCategory.business_financial: "Business & Financial",
    DocumentCategory.medical_healthcare: "Medical & Healthcare",
    DocumentCategory.legal: "Legal",
    DocumentCategory.educational: "Educational",
    DocumentCategory.administrative_hr: "Administrative & HR",
    DocumentCategory.logistics_supply_chain: "Logistics & Supply Chain",
    DocumentCategory.government_identity: "Government & Identity",
    DocumentCategory.media_content: "Media & Content",
    DocumentCategory.technical_data: "Technical & Data",
    DocumentCategory.image_based: "Image-Based",
    DocumentCategory.communication: "Communication",
    DocumentCategory.other: "Other",
}

# Sub-types per category — used by the LLM classifier prompt
CATEGORY_SUBTYPES: dict[DocumentCategory, list[str]] = {
    DocumentCategory.business_financial: [
        "invoice", "receipt", "quotation", "purchase_order", "delivery_note",
        "expense_report", "financial_statement", "balance_sheet", "income_statement",
        "cash_flow_statement", "bank_statement", "payroll_record", "tax_document",
    ],
    DocumentCategory.medical_healthcare: [
        "patient_record", "prescription", "lab_result", "medical_report",
        "discharge_summary", "imaging_report", "insurance_claim", "appointment_record",
    ],
    DocumentCategory.legal: [
        "contract", "agreement", "court_document", "affidavit",
        "will", "license", "compliance_document",
    ],
    DocumentCategory.educational: [
        "certificate", "transcript", "report_card", "research_paper",
        "assignment", "lecture_notes", "exam",
    ],
    DocumentCategory.administrative_hr: [
        "employee_record", "cv_resume", "job_application", "offer_letter",
        "performance_review", "attendance_record", "policy_manual",
    ],
    DocumentCategory.logistics_supply_chain: [
        "bill_of_lading", "shipping_label", "packing_list", "delivery_receipt",
        "customs_declaration", "inventory_report",
    ],
    DocumentCategory.government_identity: [
        "national_id", "passport", "drivers_license", "birth_certificate",
        "permit", "tax_certificate",
    ],
    DocumentCategory.media_content: [
        "article", "blog_post", "script", "book", "news_report", "marketing_content",
    ],
    DocumentCategory.technical_data: [
        "spreadsheet", "database_export", "api_documentation",
        "system_log", "blueprint", "data_report",
    ],
    DocumentCategory.image_based: [
        "scanned_document", "receipt_photo", "whiteboard_notes",
        "handwritten_notes", "filled_form",
    ],
    DocumentCategory.communication: [
        "email", "chat_log", "meeting_minutes", "memo",
    ],
    DocumentCategory.other: ["unknown"],
}
