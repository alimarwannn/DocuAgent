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