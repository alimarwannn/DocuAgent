from pathlib import Path

import src.database as database

from src.database import (
    create_tables,
    get_document,
    get_document_fields,
    list_review_documents,
)

from src.document_service import (
    approve_reviewed_document,
    reject_reviewed_document,
    save_processed_document,
)


TEST_DATABASE = Path(
    "data/test_review_workflow.db"
)

if TEST_DATABASE.exists():
    TEST_DATABASE.unlink()

database.DATABASE_PATH = TEST_DATABASE

create_tables()


pending_result = save_processed_document(
    filename="review_test_invoice.jpg",
    raw_ocr_text="Invoice REVIEW-001",
    scan_result={
        "document_type": "invoice",
        "scan_mode": "full",
        "fields": {
            "supplier_name": "Vodafone Egypt",
            "invoice_number": "REVIEW-001",
            "date": "2026-08-11",
            "customer": "Test Customer",
            "subtotal": 1000,
            "tax": 140,
            "total": 1200,
            "currency": "EGP",
        },
    },
)

pending_id = pending_result[
    "document_id"
]

assert (
    pending_result["review_status"]
    == "pending_review"
)


queue = list_review_documents()

assert any(
    document["id"] == pending_id
    for document in queue
)


approval = approve_reviewed_document(
    pending_id,
    edited_fields={
        "total": 1140,
    },
    note=(
        "Corrected total after "
        "manual review."
    ),
)

assert approval["success"] is True

assert (
    approval["review_status"]
    == "approved"
)


document = get_document(
    pending_id
)

assert (
    document["review_status"]
    == "approved"
)


fields = get_document_fields(
    pending_id
)

assert float(fields["total"]) == 1140.0


reject_result = save_processed_document(
    filename="review_reject_test.jpg",
    raw_ocr_text="Invoice REVIEW-002",
    scan_result={
        "document_type": "invoice",
        "scan_mode": "full",
        "fields": {
            "supplier_name": "Vodafone Egypt",
            "invoice_number": "REVIEW-002",
            "date": "2026-08-11",
            "customer": "Test Customer",
            "subtotal": 500,
            "tax": 70,
            "total": 999,
            "currency": "EGP",
        },
    },
)

reject_id = reject_result[
    "document_id"
]


rejection = reject_reviewed_document(
    reject_id,
    note=(
        "Document rejected "
        "during review."
    ),
)

assert rejection["success"] is True

assert (
    get_document(
        reject_id
    )["review_status"]
    == "rejected"
)


queue = list_review_documents()

assert not any(
    document["id"] == pending_id
    for document in queue
)

assert not any(
    document["id"] == reject_id
    for document in queue
)


if TEST_DATABASE.exists():
    TEST_DATABASE.unlink()


print(
    "Human review workflow tests passed."
)