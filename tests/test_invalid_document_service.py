from src.database import get_database_connection
from src.document_service import save_processed_document

scan_result = {
    "document_type": "invoice",
    "scan_mode": "full",
    "fields": {
        "supplier_name": "Vodafone Egypt",
        "invoice_number": None,
        "date": "05/08/2026",
        "customer": None,
        "subtotal": 1000,
        "tax": 140,
        "total": 1200,
        "currency": "ABC",
    },
}

saved_result = save_processed_document(
    filename="invalid_service_invoice.jpg",
    raw_ocr_text="TAX INVOICE",
    scan_result=scan_result,
)

assert saved_result is not None
assert len(saved_result["validation_issues"]) == 4

document_id = saved_result["document_id"]

connection = get_database_connection()
cursor = connection.cursor()

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

assert issue_count == 4

print("Invalid document service test passed.")
print(saved_result)