from uuid import uuid4

from src.document_service import save_processed_document
from src.database import get_document, get_document_fields


invoice_number = f"SERVICE-{uuid4().hex[:8].upper()}"

scan_result = {
    "document_type": "invoice",
    "scan_mode": "full",
    "fields": {
        "supplier_name": "Vodafone Egypt",
        "invoice_number": invoice_number,
        "date": "2026-08-10",
        "customer": None,
        "subtotal": 1000,
        "tax": 140,
        "total": 1140,
        "currency": "EGP",
    },
}

saved_result = save_processed_document(
    filename="samples/service_test.jpg",
    raw_ocr_text="Test invoice OCR text",
    scan_result=scan_result,
)

assert saved_result is not None
assert "document_id" in saved_result
assert saved_result["validation_issues"] == []

document_id = saved_result["document_id"]

document = get_document(document_id)
fields = get_document_fields(document_id)

assert document is not None
assert document["document_type"] == "invoice"
assert document["scan_mode"] == "full"
assert fields["invoice_number"] == invoice_number

print(
    "Document service test passed.",
    saved_result,
)