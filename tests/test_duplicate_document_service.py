from src.document_service import save_processed_document

first_scan = {
    "document_type": "invoice",
    "scan_mode": "full",
    "fields": {
        "supplier_name": "Vodafone Egypt",
        "invoice_number": "SERVICE-DUP-001",
        "date": "2026-08-05",
        "customer": None,
        "subtotal": 1000,
        "tax": 140,
        "total": 1140,
        "currency": "EGP",
    },
}

second_scan = {
    "document_type": "invoice",
    "scan_mode": "full",
    "fields": first_scan["fields"].copy(),
}

first_result = save_processed_document(
    filename="duplicate_service_1.jpg",
    raw_ocr_text="Invoice No: SERVICE-DUP-001",
    scan_result=first_scan,
)

second_result = save_processed_document(
    filename="duplicate_service_2.jpg",
    raw_ocr_text="Invoice No: SERVICE-DUP-001",
    scan_result=second_scan,
)

assert first_result is not None
assert second_result is not None

first_issue_types = [
    issue["issue_type"]
    for issue in first_result["validation_issues"]
]

second_issue_types = [
    issue["issue_type"]
    for issue in second_result["validation_issues"]
]

assert "duplicate_invoice" not in first_issue_types
assert "duplicate_invoice" in second_issue_types

print("Duplicate document service test passed.")
print(second_result)