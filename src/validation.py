from datetime import datetime

from src.schemas import (
    INVOICE_REQUIRED_FIELDS,
    RECEIPT_REQUIRED_FIELDS,
)


ALLOWED_CURRENCIES = {
    "EGP",
    "USD",
    "EUR",
    "GBP",
    "QAR",
    "SAR",
}


def validate_required_fields(fields, document_type):
    if document_type == "invoice":
        required_fields = INVOICE_REQUIRED_FIELDS
    elif document_type == "receipt":
        required_fields = RECEIPT_REQUIRED_FIELDS
    else:
        return [
            {
                "issue_type": "unknown_document_type",
                "message": f"Unsupported document type: {document_type}",
                "severity": "error",
            }
        ]

    issues = []

    for field in required_fields:
        value = fields.get(field)

        if value is None or value == "":
            issues.append(
                {
                    "issue_type": "missing_field",
                    "message": f"Required field {field} is missing.",
                    "severity": "error",
                }
            )

    return issues


def validate_positive_amounts(fields):
    issues = []

    for field_name in ["subtotal", "tax", "total"]:
        value = fields.get(field_name)

        if value is None:
            continue

        if not isinstance(value, (int, float)):
            issues.append(
                {
                    "issue_type": "invalid_amount",
                    "message": f"Field {field_name} must be numeric.",
                    "severity": "error",
                }
            )
            continue

        if value < 0:
            issues.append(
                {
                    "issue_type": "invalid_amount",
                    "message": f"Field {field_name} cannot be negative.",
                    "severity": "error",
                }
            )

    return issues


def validate_total_consistency(fields):
    subtotal = fields.get("subtotal")
    tax = fields.get("tax")
    total = fields.get("total")

    if not all(
        isinstance(value, (int, float))
        for value in [subtotal, tax, total]
    ):
        return []

    expected_total = subtotal + tax

    if abs(expected_total - total) > 0.01:
        return [
            {
                "issue_type": "total_mismatch",
                "message": (
                    f"Subtotal plus tax is {expected_total}, "
                    f"but total is {total}."
                ),
                "severity": "error",
            }
        ]

    return []


def validate_currency(fields):
    currency = fields.get("currency")

    if currency is None or currency == "":
        return []

    if currency not in ALLOWED_CURRENCIES:
        return [
            {
                "issue_type": "invalid_currency",
                "message": f"Unsupported currency: {currency}.",
                "severity": "error",
            }
        ]

    return []


def validate_date(fields):
    date_value = fields.get("date")

    if date_value is None or date_value == "":
        return []

    try:
        datetime.strptime(date_value, "%Y-%m-%d")
    except ValueError:
        return [
            {
                "issue_type": "invalid_date",
                "message": (
                    f"Invalid date: {date_value}. "
                    "Expected YYYY-MM-DD."
                ),
                "severity": "error",
            }
        ]

    return []


def validate_document(fields, document_type):
    issues = []

    issues.extend(
        validate_required_fields(
            fields,
            document_type,
        )
    )

    issues.extend(validate_positive_amounts(fields))
    issues.extend(validate_total_consistency(fields))
    issues.extend(validate_currency(fields))
    issues.extend(validate_date(fields))

    return issues


def validate_scan_result(fields, document_type, scan_mode):
    if scan_mode == "quick":
        return []

    if scan_mode == "full":
        return validate_document(
            fields,
            document_type,
        )

    if scan_mode == "partial":
        issues = []

        issues.extend(validate_positive_amounts(fields))
        issues.extend(validate_total_consistency(fields))
        issues.extend(validate_currency(fields))
        issues.extend(validate_date(fields))

        return issues

    return [
        {
            "issue_type": "invalid_scan_mode",
            "message": f"Unsupported scan mode: {scan_mode}",
            "severity": "error",
        }
    ]