from uuid import uuid4

from src.business_tools import (
    average_document_value,
    detect_contradictions,
    duplicate_invoices,
    highest_value_documents,
    invalid_documents,
    supplier_summary,
    total_spend,
    total_tax,
)
from src.database import (
    create_tables,
    save_document,
    save_extracted_fields,
    save_validation_issues,
)


create_tables()

unique_id = uuid4().hex[:8]


real_conflict_number = f"CONFLICT-{unique_id}"

first_document_id = save_document(
    filename=f"conflict_1_{unique_id}.jpg",
    document_type="invoice",
    scan_mode="full",
    raw_ocr_text="Conflict test",
)

save_extracted_fields(
    first_document_id,
    {
        "supplier_name": "Vodafone Egypt",
        "invoice_number": real_conflict_number,
        "date": "2026-08-10",
        "subtotal": 1000,
        "tax": 140,
        "total": 1140,
        "currency": "EGP",
    },
)


second_document_id = save_document(
    filename=f"conflict_2_{unique_id}.jpg",
    document_type="invoice",
    scan_mode="full",
    raw_ocr_text="Conflict test",
)

save_extracted_fields(
    second_document_id,
    {
        "supplier_name": "Vodafone Qatar",
        "invoice_number": real_conflict_number,
        "date": "2026-08-09",
        "subtotal": 1200,
        "tax": 168,
        "total": 1368,
        "currency": "EGP",
    },
)

save_validation_issues(
    second_document_id,
    [
        {
            "issue_type": "duplicate_invoice",
            "message": "Duplicate invoice number detected.",
            "severity": "error",
        }
    ],
)


equivalent_number = f"EQUIVALENT-{unique_id}"

third_document_id = save_document(
    filename=f"equivalent_1_{unique_id}.jpg",
    document_type="invoice",
    scan_mode="full",
    raw_ocr_text="Equivalent values test",
)

save_extracted_fields(
    third_document_id,
    {
        "supplier_name": "Vodafone Egypt",
        "invoice_number": equivalent_number,
        "date": "15/01/2019 11:05.16 AM",
        "total": "193.0",
        "currency": "SAR",
    },
)


fourth_document_id = save_document(
    filename=f"equivalent_2_{unique_id}.jpg",
    document_type="invoice",
    scan_mode="full",
    raw_ocr_text="Equivalent values test",
)

save_extracted_fields(
    fourth_document_id,
    {
        "supplier_name": "vodafone   egypt",
        "invoice_number": equivalent_number,
        "date": "2019-01-15",
        "total": "193.00",
        "currency": "SAR",
    },
)


spend = total_spend(
    start_date="2026-08-09",
    end_date="2026-08-10",
)

assert spend["total"] >= 2508


tax = total_tax(
    start_date="2026-08-09",
    end_date="2026-08-10",
)

assert tax["total_tax"] >= 308


average = average_document_value(
    start_date="2026-08-09",
    end_date="2026-08-10",
)

assert average["average"] > 0


highest = highest_value_documents(limit=5)

assert isinstance(highest, list)
assert len(highest) > 0


suppliers = supplier_summary()

assert len(suppliers) > 0


invalid = invalid_documents()

assert any(
    document["id"] == second_document_id
    for document in invalid
)


duplicates = duplicate_invoices()

assert any(
    duplicate["invoice_number"] == real_conflict_number
    for duplicate in duplicates
)


contradictions = detect_contradictions()


assert any(
    contradiction["invoice_number"] == real_conflict_number
    and contradiction["type"] == "conflicting_total"
    for contradiction in contradictions
)

assert any(
    contradiction["invoice_number"] == real_conflict_number
    and contradiction["type"] == "conflicting_supplier"
    for contradiction in contradictions
)

assert any(
    contradiction["invoice_number"] == real_conflict_number
    and contradiction["type"] == "conflicting_date"
    for contradiction in contradictions
)


equivalent_contradictions = [
    contradiction
    for contradiction in contradictions
    if contradiction["invoice_number"] == equivalent_number
]

assert equivalent_contradictions == []


print("Zaki normalized business tool tests passed.")