from src.database import (
    get_document,
    get_document_fields,
    get_document_issues,
)
from src.document_service import save_processed_document

scan_result = {
    "document_type": "invoice",
    "scan_mode": "full",
    "fields": {
        "supplier_name": "Vodafone Egypt",
        "invoice_number": "QUERY-001",
        "date": "2026-08-05",
        "customer": None,
        "subtotal": 1000,
        "tax": 140,
        "total": 1200,
        "currency": "EGP",
    },
}

saved_result = save_processed_document(
    filename="query_test_invoice.jpg",
    raw_ocr_text="Invoice No: QUERY-001",
    scan_result=scan_result,
)

document_id = saved_result["document_id"]

document = get_document(document_id)
fields = get_document_fields(document_id)
issues = get_document_issues(document_id)

assert document is not None
assert document["filename"] == "query_test_invoice.jpg"
assert document["document_type"] == "invoice"

assert fields["invoice_number"] == "QUERY-001"
assert fields["total"] == "1200"

assert len(issues) == 1
assert issues[0]["issue_type"] == "total_mismatch"

print("Database query helper tests passed.")
print(dict(document))
print(fields)
print(issues)