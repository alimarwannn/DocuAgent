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
    "MYR",
}


def _is_number(value):
    return (
        isinstance(
            value,
            (int, float),
        )
        and not isinstance(
            value,
            bool,
        )
    )


def _deduplicate_issues(
    issues,
):
    seen = set()
    result = []

    for issue in issues:
        key = (
            issue.get(
                "issue_type"
            ),
            issue.get(
                "message"
            ),
            issue.get(
                "severity"
            ),
        )

        if key in seen:
            continue

        seen.add(
            key
        )

        result.append(
            issue
        )

    return result


def validate_required_fields(
    fields,
    document_type,
):
    if document_type == "invoice":
        required_fields = (
            INVOICE_REQUIRED_FIELDS
        )

    elif document_type == "receipt":
        required_fields = (
            RECEIPT_REQUIRED_FIELDS
        )

    else:
        return [
            {
                "issue_type":
                    "unknown_document_type",

                "message":
                    (
                        "Unsupported "
                        f"document type: "
                        f"{document_type}"
                    ),

                "severity":
                    "error",
            }
        ]

    issues = []

    for field in required_fields:
        value = fields.get(
            field
        )

        if value in (
            None,
            "",
        ):
            issues.append(
                {
                    "issue_type":
                        "missing_field",

                    "message":
                        (
                            field
                            .replace(
                                "_",
                                " ",
                            )
                            .title()
                            + " is missing."
                        ),

                    "severity":
                        "error",
                }
            )

    return issues


def validate_positive_amounts(
    fields,
):
    issues = []

    for field_name in [
        "subtotal",
        "tax",
        "total",
    ]:
        value = fields.get(
            field_name
        )

        if value is None:
            continue

        if not _is_number(
            value
        ):
            issues.append(
                {
                    "issue_type":
                        "invalid_amount",

                    "message":
                        (
                            field_name
                            .replace(
                                "_",
                                " ",
                            )
                            .title()
                            + " must be numeric."
                        ),

                    "severity":
                        "error",
                }
            )

            continue

        if value < 0:
            issues.append(
                {
                    "issue_type":
                        "invalid_amount",

                    "message":
                        (
                            field_name
                            .replace(
                                "_",
                                " ",
                            )
                            .title()
                            + " cannot be negative."
                        ),

                    "severity":
                        "error",
                }
            )

    total = fields.get(
        "total"
    )

    if (
        _is_number(total)
        and total <= 0
    ):
        issues.append(
            {
                "issue_type":
                    "invalid_total",

                "message":
                    (
                        "Total must be "
                        "greater than zero."
                    ),

                "severity":
                    "error",
            }
        )

    return issues


def validate_total_consistency(
    fields,
):
    subtotal = fields.get(
        "subtotal"
    )

    tax = fields.get(
        "tax"
    )

    total = fields.get(
        "total"
    )

    if not all(
        _is_number(
            value
        )
        for value
        in [
            subtotal,
            tax,
            total,
        ]
    ):
        return []

    expected_total = (
        subtotal
        + tax
    )

    if abs(
        expected_total
        - total
    ) > 0.01:
        return [
            {
                "issue_type":
                    "total_mismatch",

                "message":
                    (
                        f"Subtotal plus tax is "
                        f"{expected_total}, "
                        f"but total is "
                        f"{total}."
                    ),

                "severity":
                    "error",
            }
        ]

    return []


def validate_financial_completeness(
    fields,
    document_type,
):
    issues = []

    total = fields.get(
        "total"
    )

    currency = fields.get(
        "currency"
    )

    if total in (
        None,
        "",
    ):
        issues.append(
            {
                "issue_type":
                    "missing_total",

                "message":
                    (
                        "Total could not be "
                        "verified from the document."
                    ),

                "severity":
                    "error",
            }
        )

    if currency in (
        None,
        "",
    ):
        issues.append(
            {
                "issue_type":
                    "missing_currency",

                "message":
                    (
                        "Currency could not be "
                        "verified from the document."
                    ),

                "severity":
                    "error",
            }
        )

    subtotal = fields.get(
        "subtotal"
    )

    tax = fields.get(
        "tax"
    )

    if (
        tax is not None
        and subtotal is None
    ):
        issues.append(
            {
                "issue_type":
                    "incomplete_amount_breakdown",

                "message":
                    (
                        "Tax was found but subtotal "
                        "was not found, so the total "
                        "cannot be fully cross-checked."
                    ),

                "severity":
                    "warning",
            }
        )

    if (
        document_type == "invoice"
        and subtotal is None
    ):
        issues.append(
            {
                "issue_type":
                    "missing_subtotal",

                "message":
                    (
                        "Invoice subtotal could "
                        "not be verified."
                    ),

                "severity":
                    "warning",
            }
        )

    return issues


def validate_currency(
    fields,
):
    currency = fields.get(
        "currency"
    )

    if currency in (
        None,
        "",
    ):
        return []

    if not isinstance(
        currency,
        str,
    ):
        return [
            {
                "issue_type":
                    "invalid_currency",

                "message":
                    "Currency must be text.",

                "severity":
                    "error",
            }
        ]

    normalized = (
        currency
        .strip()
        .upper()
    )

    if normalized == "RM":
        normalized = "MYR"

    if (
        normalized
        not in ALLOWED_CURRENCIES
    ):
        return [
            {
                "issue_type":
                    "invalid_currency",

                "message":
                    (
                        "Unsupported currency: "
                        f"{currency}."
                    ),

                "severity":
                    "error",
            }
        ]

    return []


def validate_date(
    fields,
):
    date_value = fields.get(
        "date"
    )

    if date_value in (
        None,
        "",
    ):
        return []

    if not isinstance(
        date_value,
        str,
    ):
        return [
            {
                "issue_type":
                    "invalid_date",

                "message":
                    (
                        "Date must use "
                        "YYYY-MM-DD format."
                    ),

                "severity":
                    "error",
            }
        ]

    try:
        datetime.strptime(
            date_value,
            "%Y-%m-%d",
        )

    except ValueError:
        return [
            {
                "issue_type":
                    "invalid_date",

                "message":
                    (
                        f"Invalid date: "
                        f"{date_value}. "
                        "Expected YYYY-MM-DD."
                    ),

                "severity":
                    "error",
            }
        ]

    return []


def validate_document(
    fields,
    document_type,
):
    issues = []

    issues.extend(
        validate_required_fields(
            fields,
            document_type,
        )
    )

    issues.extend(
        validate_positive_amounts(
            fields
        )
    )

    issues.extend(
        validate_total_consistency(
            fields
        )
    )

    issues.extend(
        validate_financial_completeness(
            fields,
            document_type,
        )
    )

    issues.extend(
        validate_currency(
            fields
        )
    )

    issues.extend(
        validate_date(
            fields
        )
    )

    return _deduplicate_issues(
        issues
    )


def validate_scan_result(
    fields,
    document_type,
    scan_mode,
):
    if scan_mode == "quick":
        return []

    if scan_mode == "full":
        return validate_document(
            fields,
            document_type,
        )

    if scan_mode == "partial":
        issues = []

        issues.extend(
            validate_positive_amounts(
                fields
            )
        )

        issues.extend(
            validate_total_consistency(
                fields
            )
        )

        issues.extend(
            validate_currency(
                fields
            )
        )

        issues.extend(
            validate_date(
                fields
            )
        )

        return _deduplicate_issues(
            issues
        )

    return [
        {
            "issue_type":
                "invalid_scan_mode",

            "message":
                (
                    "Unsupported scan mode: "
                    f"{scan_mode}"
                ),

            "severity":
                "error",
        }
    ]