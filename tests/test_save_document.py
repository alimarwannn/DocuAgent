from src.database import create_tables, get_database_connection, save_document

create_tables()

document_id = save_document(
    filename="invoice_1.jpg",
    document_type="invoice",
    scan_mode="full",
    raw_ocr_text="TAX INVOICE Total: 1140 EGP",
)

assert isinstance(document_id, int)
assert document_id > 0

connection = get_database_connection()
cursor = connection.cursor()

cursor.execute(
    """
    SELECT filename, document_type, scan_mode, raw_ocr_text
    FROM documents
    WHERE id = ?
    """,
    (document_id,),
)

saved_document = cursor.fetchone()
connection.close()

assert saved_document is not None
assert saved_document["filename"] == "invoice_1.jpg"
assert saved_document["document_type"] == "invoice"
assert saved_document["scan_mode"] == "full"
assert saved_document["raw_ocr_text"] == "TAX INVOICE Total: 1140 EGP"

print("Save document test passed.")
print(f"Document ID: {document_id}")