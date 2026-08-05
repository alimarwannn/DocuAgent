from src.database import (
    create_tables,
    invoice_number_exists,
    save_document,
    save_extracted_fields,
)

create_tables()

document_id = save_document(
    filename="duplicate_test_invoice.jpg",
    document_type="invoice",
    scan_mode="full",
    raw_ocr_text="Invoice No: DUP-001",
)

save_extracted_fields(
    document_id,
    {
        "invoice_number": "DUP-001",
    },
)

assert invoice_number_exists("DUP-001") is True
assert invoice_number_exists("NEW-999") is False
assert invoice_number_exists(None) is False
assert invoice_number_exists("") is False

print("Duplicate invoice lookup tests passed.")