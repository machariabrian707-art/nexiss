from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from nexiss.db.models.document import DocumentStatus
from nexiss.db.models.document_type import DocumentType
from nexiss.db.models.processing_job import ProcessingJobStatus


class DocumentCreateRequest(BaseModel):
    file_name: str = Field(min_length=1, max_length=255)
    content_type: str
    storage_key: str = Field(min_length=1, max_length=1024)
    # User tells us what kind of doc this is before processing
    declared_type: DocumentType | None = Field(
        default=None,
        description="The document category declared by the uploader. "
                    "If omitted the AI pipeline will infer it."
    )


class DocumentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    org_id: UUID
    created_by_user_id: UUID | None
    file_name: str
    content_type: str
    storage_key: str
    status: DocumentStatus
    declared_type: str | None
    confirmed_type: str | None
    type_confidence: float | None
    page_count: int | None
    extracted_data: dict | None
    confidence_score: float | None
    processing_attempts: int
    last_error: str | None
    created_at: datetime
    updated_at: datetime


class DocumentProcessResponse(BaseModel):
    document_id: UUID
    status: DocumentStatus
    task_id: str
    job_id: UUID


class DocumentProgressResponse(BaseModel):
    job_id: UUID
    document_id: UUID
    status: ProcessingJobStatus
    progress_percentage: int
    current_step: str
    error_message: str | None
    task_id: str
    updated_at: datetime


# ---------------------------------------------------------------------------
# Domain-specific extraction schemas
# These define the structured shape of extracted_data per document type.
# The LLM is prompted to return data matching these shapes.
# ---------------------------------------------------------------------------

class InvoiceData(BaseModel):
    vendor_name: str | None = None
    vendor_address: str | None = None
    invoice_number: str | None = None
    invoice_date: str | None = None
    due_date: str | None = None
    line_items: list[dict[str, Any]] = Field(default_factory=list)
    subtotal: float | None = None
    tax: float | None = None
    total_amount: float | None = None
    currency: str | None = None
    payment_terms: str | None = None


class MedicalRecordData(BaseModel):
    patient_name: str | None = None
    patient_id: str | None = None
    date_of_birth: str | None = None
    visit_date: str | None = None
    doctor_name: str | None = None
    facility: str | None = None
    diagnosis: list[str] = Field(default_factory=list)
    medications: list[str] = Field(default_factory=list)
    lab_values: dict[str, Any] = Field(default_factory=dict)
    notes: str | None = None


class LegalDocumentData(BaseModel):
    document_title: str | None = None
    parties: list[str] = Field(default_factory=list)
    effective_date: str | None = None
    expiry_date: str | None = None
    jurisdiction: str | None = None
    key_clauses: list[str] = Field(default_factory=list)
    risk_flags: list[str] = Field(default_factory=list)
    obligations: list[str] = Field(default_factory=list)


class HRDocumentData(BaseModel):
    employee_name: str | None = None
    employee_id: str | None = None
    job_title: str | None = None
    department: str | None = None
    date: str | None = None
    skills: list[str] = Field(default_factory=list)
    salary: float | None = None
    currency: str | None = None
    notes: str | None = None


class LogisticsDocumentData(BaseModel):
    shipper: str | None = None
    consignee: str | None = None
    tracking_number: str | None = None
    origin: str | None = None
    destination: str | None = None
    ship_date: str | None = None
    estimated_delivery: str | None = None
    items: list[dict[str, Any]] = Field(default_factory=list)
    total_weight: float | None = None
    total_value: float | None = None


class IdentityDocumentData(BaseModel):
    full_name: str | None = None
    document_number: str | None = None
    nationality: str | None = None
    date_of_birth: str | None = None
    issue_date: str | None = None
    expiry_date: str | None = None
    issuing_authority: str | None = None


# Map DocumentType -> extraction schema class (used by LLM service)
DOC_TYPE_SCHEMA_MAP: dict[str, type[BaseModel]] = {
    "invoice": InvoiceData,
    "receipt": InvoiceData,
    "quotation": InvoiceData,
    "purchase_order": InvoiceData,
    "patient_record": MedicalRecordData,
    "prescription": MedicalRecordData,
    "lab_result": MedicalRecordData,
    "medical_report": MedicalRecordData,
    "discharge_summary": MedicalRecordData,
    "imaging_report": MedicalRecordData,
    "contract": LegalDocumentData,
    "agreement": LegalDocumentData,
    "affidavit": LegalDocumentData,
    "employee_record": HRDocumentData,
    "cv_resume": HRDocumentData,
    "offer_letter": HRDocumentData,
    "performance_review": HRDocumentData,
    "bill_of_lading": LogisticsDocumentData,
    "delivery_note": LogisticsDocumentData,
    "delivery_receipt": LogisticsDocumentData,
    "packing_list": LogisticsDocumentData,
    "national_id": IdentityDocumentData,
    "passport": IdentityDocumentData,
    "drivers_license": IdentityDocumentData,
    "birth_certificate": IdentityDocumentData,
}
