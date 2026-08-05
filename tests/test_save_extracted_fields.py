from src.database import (
    create_tables,
    get_database_connection,
    save_document,
    save_extracted_fields,
)

create_tables()

document_id = save_document(
    filename="invoice_fields_test.jpg",
    document_type="invoice",
    scan_mode="full",
    raw_ocr_text="TAX INVOICE Total: 1140 EGP",
)

fields = {
    "invoice_number": "INV-123",
    "total": 1140,
    "currency": "EGP",
    "customer": None,
}

save_extracted_fields(document_id, fields)

connection = get_database_connection()
cursor = connection.cursor()

cursor.execute(
    """
    SELECT field_name, field_value
    FROM extracted_fields
    WHERE document_id = ?
    """,
    (document_id,),
)

saved_rows = cursor.fetchall()
connection.close()

saved_fields = {
    row["field_name"]: row["field_value"]
    for row in saved_rows
}

assert saved_fields["invoice_number"] == "INV-123"
assert saved_fields["total"] == "1140"
assert saved_fields["currency"] == "EGP"
assert saved_fields["customer"] is None

print("Save extracted fields test passed.")
print(saved_fields)