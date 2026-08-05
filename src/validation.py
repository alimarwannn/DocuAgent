from datetime import datetime

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

ALLOWED_CURRENCIES = {
    "EGP",
    "USD",
    "EUR",
    "GBP",
    "QAR",
}


def validate_currency(fields):
    if not isinstance(fields, dict):
        return []

    currency = fields.get("currency")

    if currency in (None, ""):
        return []

    if not isinstance(currency, str):
        return [{
            "issue_type": "invalid_currency",
            "message": "Currency must be text.",
            "severity": "error",
        }]

    normalized_currency = currency.strip().upper()

    if normalized_currency not in ALLOWED_CURRENCIES:
        return [{
            "issue_type": "invalid_currency",
            "message": f"Unsupported currency: {currency}.",
            "severity": "error",
        }]

    return []

def validate_date(fields):
    if not isinstance(fields, dict):
        return []

    date_value = fields.get("date")

    if date_value in (None, ""):
        return []

    if not isinstance(date_value, str):
        return [{
            "issue_type": "invalid_date",
            "message": "Date must be text in YYYY-MM-DD format.",
            "severity": "error",
        }]

    try:
        datetime.strptime(date_value.strip(), "%Y-%m-%d")
    except ValueError:
        return [{
            "issue_type": "invalid_date",
            "message": f"Invalid date: {date_value}. Expected YYYY-MM-DD.",
            "severity": "error",
        }]

    return []

def validate_document(fields, document_type):
    issues = []

    issues.extend(
        validate_required_fields(fields, document_type)
    )
    issues.extend(
        validate_positive_amounts(fields)
    )
    issues.extend(
        validate_total_consistency(fields)
    )
    issues.extend(
        validate_currency(fields)
    )
    issues.extend(
        validate_date(fields)
    )

    return issues