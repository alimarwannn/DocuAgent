from src.database import get_database_connection
from src.document_service import save_processed_document

scan_result = {
    "document_type": "invoice",
    "scan_mode": "full",
    "fields": {
        "supplier_name": "Vodafone Egypt",
        "invoice_number": "SERVICE-VALID-001",
        "date": "2026-08-05",
        "customer": None,
        "subtotal": 1000,
        "tax": 140,
        "total": 1140,
        "currency": "EGP",
    },
}

saved_result = save_processed_document(
    filename="service_test_invoice.jpg",
    raw_ocr_text="TAX INVOICE Invoice No: SERVICE-VALID-001 Total: 1140 EGP",
    scan_result=scan_result,
)

assert saved_result is not None
assert isinstance(saved_result["document_id"], int)
assert saved_result["validation_issues"] == []

document_id = saved_result["document_id"]

connection = get_database_connection()
cursor = connection.cursor()

cursor.execute(
    """
    SELECT filename, document_type, scan_mode
    FROM documents
    WHERE id = ?
    """,
    (document_id,),
)

saved_document = cursor.fetchone()

cursor.execute(
    """
    SELECT COUNT(*)
    FROM extracted_fields
    WHERE document_id = ?
    """,
    (document_id,),
)

field_count = cursor.fetchone()[0]

cursor.execute(
    """
    SELECT COUNT(*)
    FROM validation_issues
    WHERE document_id = ?
    """,
    (document_id,),
)

issue_count = cursor.fetchone()[0]

connection.close()

assert saved_document is not None
assert saved_document["filename"] == "service_test_invoice.jpg"
assert saved_document["document_type"] == "invoice"
assert saved_document["scan_mode"] == "full"

assert field_count == 8
assert issue_count == 0

print("Document service test passed.")
print(saved_result)