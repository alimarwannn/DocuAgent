from pathlib import Path

import src.database as database

from src.business_tools import (
    total_spend,
    total_tax,
)
from src.database import (
    create_tables,
    filter_documents_by_amount,
    save_document,
    save_extracted_fields,
)
from src.zaki_chat import (
    format_deterministic_answer,
)
from src.zaki_router import select_zaki_tool


TEST_DATABASE = Path("data/test_currency_aware_analytics.db")

if TEST_DATABASE.exists():
    TEST_DATABASE.unlink()

database.DATABASE_PATH = TEST_DATABASE

create_tables()


approved_egp = save_document(
    filename="approved-egp.jpg",
    document_type="invoice",
    scan_mode="full",
    raw_ocr_text="Approved EGP invoice",
    review_status="approved",
)

save_extracted_fields(
    approved_egp,
    {
        "supplier_name": "Vodafone Egypt",
        "invoice_number": "CUR-001",
        "date": "2026-08-10",
        "tax": 140,
        "total": 1140,
        "currency": "EGP",
    },
)


approved_usd = save_document(
    filename="approved-usd.jpg",
    document_type="invoice",
    scan_mode="full",
    raw_ocr_text="Approved USD invoice",
    review_status="approved",
)

save_extracted_fields(
    approved_usd,
    {
        "supplier_name": "OpenAI",
        "invoice_number": "CUR-002",
        "date": "2026-08-10",
        "tax": 20,
        "total": 120,
        "currency": "USD",
    },
)


pending_egp = save_document(
    filename="pending-egp.jpg",
    document_type="invoice",
    scan_mode="full",
    raw_ocr_text="Pending EGP invoice",
    review_status="pending_review",
)

save_extracted_fields(
    pending_egp,
    {
        "supplier_name": "Pending Supplier",
        "invoice_number": "CUR-003",
        "date": "2026-08-10",
        "tax": 999,
        "total": 9999,
        "currency": "EGP",
    },
)


rejected_egp = save_document(
    filename="rejected-egp.jpg",
    document_type="invoice",
    scan_mode="full",
    raw_ocr_text="Rejected EGP invoice",
    review_status="rejected",
)

save_extracted_fields(
    rejected_egp,
    {
        "supplier_name": "Rejected Supplier",
        "invoice_number": "CUR-004",
        "date": "2026-08-10",
        "tax": 500,
        "total": 5000,
        "currency": "EGP",
    },
)


spend = total_spend(
    start_date="2026-08-10",
    end_date="2026-08-10",
)

assert spend["document_count"] == 2
assert spend["currency"] is None
assert spend["totals_by_currency"] == {
    "EGP": 1140.0,
    "USD": 120.0,
}


tax = total_tax(
    start_date="2026-08-10",
    end_date="2026-08-10",
)

assert tax["document_count"] == 2
assert tax["currency"] is None
assert tax["totals_by_currency"] == {
    "EGP": 140.0,
    "USD": 20.0,
}


egp_documents = filter_documents_by_amount(
    minimum_amount=1000,
    currency="EGP",
)

assert [document["id"] for document in egp_documents] == [approved_egp]


selection = select_zaki_tool(
    "Show documents above 1000 EGP"
)

assert selection["tool_name"] == "filter_documents_by_amount"
assert selection["arguments"] == {
    "minimum_amount": 1000.0,
    "currency": "EGP",
}


answer = format_deterministic_answer(
    "How much did I spend?",
    "total_spend",
    {
        "document_count": 2,
        "currency": None,
        "totals_by_currency": {
            "EGP": 1140.0,
            "USD": 120.0,
        },
        "documents": [],
    },
)

assert "EGP" in answer
assert "USD" in answer
assert "approved" in answer.lower()


if TEST_DATABASE.exists():
    TEST_DATABASE.unlink()


print("Currency-aware analytics tests passed.")
