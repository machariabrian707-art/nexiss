"""Document type classification enum used across the Nexiss pipeline."""
from __future__ import annotations

import enum


class DocumentType(str, enum.Enum):
    # Business & Financial
    invoice = "invoice"
    receipt = "receipt"
    quotation = "quotation"
    purchase_order = "purchase_order"
    delivery_note = "delivery_note"
    expense_report = "expense_report"
    financial_statement = "financial_statement"
    bank_statement = "bank_statement"
    payroll = "payroll"
    tax_document = "tax_document"

    # Medical & Healthcare
    patient_record = "patient_record"
    prescription = "prescription"
    lab_result = "lab_result"
    medical_report = "medical_report"
    discharge_summary = "discharge_summary"
    imaging_report = "imaging_report"
    insurance_claim = "insurance_claim"
    appointment_record = "appointment_record"

    # Legal
    contract = "contract"
    agreement = "agreement"
    court_document = "court_document"
    affidavit = "affidavit"
    will = "will"
    license = "license"
    compliance_document = "compliance_document"

    # Educational
    certificate = "certificate"
    transcript = "transcript"
    report_card = "report_card"
    research_paper = "research_paper"
    assignment = "assignment"
    lecture_notes = "lecture_notes"

    # Administrative & HR
    employee_record = "employee_record"
    cv_resume = "cv_resume"
    job_application = "job_application"
    offer_letter = "offer_letter"
    performance_review = "performance_review"
    attendance_record = "attendance_record"
    policy_manual = "policy_manual"

    # Logistics & Supply Chain
    bill_of_lading = "bill_of_lading"
    shipping_label = "shipping_label"
    packing_list = "packing_list"
    delivery_receipt = "delivery_receipt"
    customs_declaration = "customs_declaration"
    inventory_report = "inventory_report"

    # Government & Identity
    national_id = "national_id"
    passport = "passport"
    drivers_license = "drivers_license"
    birth_certificate = "birth_certificate"
    permit = "permit"
    tax_certificate = "tax_certificate"

    # Communication
    email = "email"
    meeting_minutes = "meeting_minutes"
    memo = "memo"

    # Technical & Data
    spreadsheet = "spreadsheet"
    data_report = "data_report"
    system_log = "system_log"

    # Generic fallback
    unknown = "unknown"
