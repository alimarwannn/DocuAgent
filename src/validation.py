from src.schemas import (
    INVOICE_REQUIRED_FIELDS,
    RECEIPT_REQUIRED_FIELDS,
)


def validate_required_fields(fields, document_type):
    if not isinstance(fields, dict):
        return []

    if document_type == "invoice":
        required_fields = INVOICE_REQUIRED_FIELDS
    elif document_type == "receipt":
        required_fields = RECEIPT_REQUIRED_FIELDS
    else:
        return []

    issues = []

    for field in required_fields:
        if fields.get(field) in (None, ""):
            issues.append({
                "issue_type": "missing_field",
                "message": f"Required field {field} is missing.",
                "severity": "error",
            })

    return issues

def validate_positive_amounts(fields):
    if not isinstance(fields, dict):
        return []

    issues = []

    for field in ["subtotal", "tax", "total"]:
        value = fields.get(field)

        if value is None:
            continue

        if not isinstance(value, (int, float)):
            issues.append({
                "issue_type": "invalid_amount",
                "message": f"Field {field} must be numeric.",
                "severity": "error",
            })
        elif value < 0:
            issues.append({
                "issue_type": "invalid_amount",
                "message": f"Field {field} cannot be negative.",
                "severity": "error",
            })

    return issues

def validate_total_consistency(fields):
    if not isinstance(fields, dict):
        return []

    subtotal = fields.get("subtotal")
    tax = fields.get("tax")
    total = fields.get("total")

    if subtotal is None or tax is None or total is None:
        return []

    if not all(
        isinstance(value, (int, float))
        for value in [subtotal, tax, total]
    ):
        return []

    expected_total = subtotal + tax

    if abs(expected_total - total) > 0.01:
        return [{
            "issue_type": "total_mismatch",
            "message": (
                f"Subtotal plus tax equals {expected_total}, "
                f"but total is {total}."
            ),
            "severity": "error",
        }]

    return []