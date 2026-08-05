from src.validation import validate_document

valid_invoice = {
    "supplier_name": "Vodafone Egypt",
    "invoice_number": "INV-123",
    "date": "2026-08-05",
    "customer": None,
    "subtotal": 1000,
    "tax": 140,
    "total": 1140,
    "currency": "EGP",
}

invalid_invoice = {
    "supplier_name": "Vodafone Egypt",
    "invoice_number": None,
    "date": "05/08/2026",
    "customer": None,
    "subtotal": 1000,
    "tax": 140,
    "total": 1200,
    "currency": "ABC",
}

valid_issues = validate_document(
    valid_invoice,
    "invoice",
)

invalid_issues = validate_document(
    invalid_invoice,
    "invoice",
)

assert valid_issues == []
assert len(invalid_issues) == 4

issue_types = [
    issue["issue_type"]
    for issue in invalid_issues
]

assert "missing_field" in issue_types
assert "invalid_date" in issue_types
assert "total_mismatch" in issue_types
assert "invalid_currency" in issue_types

print("Combined document validation tests passed.")
print(invalid_issues)