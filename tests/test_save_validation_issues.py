from src.database import (
    create_tables,
    get_database_connection,
    save_document,
    save_validation_issues,
)

create_tables()

document_id = save_document(
    filename="invalid_invoice.jpg",
    document_type="invoice",
    scan_mode="full",
    raw_ocr_text="TAX INVOICE Total missing",
)

issues = [
    {
        "issue_type": "missing_field",
        "message": "Required field total is missing.",
        "severity": "error",
    },
    {
        "issue_type": "missing_field",
        "message": "Required field currency is missing.",
        "severity": "warning",
    },
]

save_validation_issues(document_id, issues)

connection = get_database_connection()
cursor = connection.cursor()

cursor.execute(
    """
    SELECT issue_type, message, severity
    FROM validation_issues
    WHERE document_id = ?
    """,
    (document_id,),
)

saved_issues = cursor.fetchall()
connection.close()

assert len(saved_issues) == 2
assert saved_issues[0]["issue_type"] == "missing_field"
assert saved_issues[0]["severity"] == "error"
assert saved_issues[1]["severity"] == "warning"

print("Save validation issues test passed.")