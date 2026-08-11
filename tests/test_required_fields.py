from src.validation import validate_required_fields

valid_invoice = {
    "supplier_name": "Vodafone Egypt",
    "invoice_number": "INV-123",
    "date": "2026-08-05",
    "total": 1140,
    "currency": "EGP",
}

invalid_invoice = {
    "supplier_name": "Vodafone Egypt",
    "invoice_number": None,
    "date": "",
    "total": 1140,
    "currency": None,
}

valid_issues = validate_required_fields(
    valid_invoice,
    "invoice",
)

invalid_issues = validate_required_fields(
    invalid_invoice,
    "invoice",
)

unknown_issues = validate_required_fields(
    invalid_invoice,
    "unknown",
)

assert valid_issues == []
assert len(invalid_issues) == 3
assert invalid_issues[0]["issue_type"] == "missing_field"
assert invalid_issues[0]["severity"] == "error"
assert len(unknown_issues) == 1
assert unknown_issues[0]["issue_type"] == "unknown_document_type"
assert unknown_issues[0]["severity"] == "error"

print("Required-field validation tests passed.")
print(invalid_issues)
