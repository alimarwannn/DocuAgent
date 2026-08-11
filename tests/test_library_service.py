from pathlib import Path

import src.database as database

from src.database import (
    create_tables,
    save_document,
    save_extracted_fields,
)

from src.library_service import (
    get_library_counts,
    get_pending_review_count,
    list_document_summaries,
)


TEST_DATABASE = Path(
    "data/test_library_service.db"
)

if TEST_DATABASE.exists():
    TEST_DATABASE.unlink()

database.DATABASE_PATH = (
    TEST_DATABASE
)

create_tables()


approved_id = save_document(
    filename="approved.jpg",
    document_type="invoice",
    scan_mode="full",
    raw_ocr_text="Approved invoice",
    review_status="approved",
)

save_extracted_fields(
    approved_id,
    {
        "supplier_name":
            "Vodafone Egypt",
        "invoice_number":
            "LIB-001",
        "date":
            "2026-08-11",
        "total":
            1140,
        "currency":
            "EGP",
    },
)


review_id = save_document(
    filename="review.jpg",
    document_type="invoice",
    scan_mode="full",
    raw_ocr_text="Review invoice",
    review_status="pending_review",
)

save_extracted_fields(
    review_id,
    {
        "supplier_name":
            "Test Supplier",
        "invoice_number":
            "LIB-002",
        "date":
            "2026-08-11",
        "total":
            500,
        "currency":
            "EGP",
    },
)


summaries = (
    list_document_summaries()
)

assert len(summaries) == 2

approved = next(
    item
    for item in summaries
    if item["id"]
    == approved_id
)

assert (
    approved["party"]
    == "Vodafone Egypt"
)

assert (
    approved[
        "document_number"
    ]
    == "LIB-001"
)

assert (
    approved["total"]
    == "1140"
)


counts = (
    get_library_counts()
)

assert counts["total"] == 2
assert counts["approved"] == 1

assert (
    counts["pending_review"]
    == 1
)

assert (
    get_pending_review_count()
    == 1
)


if TEST_DATABASE.exists():
    TEST_DATABASE.unlink()


print(
    "Library service tests passed."
)