from src.database import (
    create_tables,
    get_document,
    get_document_fields,
    invoice_number_exists,
    replace_extracted_fields,
    replace_validation_issues,
    save_document,
    save_extracted_fields,
    save_validation_issues,
    set_document_review_status,
)

from src.validation import (
    validate_scan_result,
)


NUMERIC_FIELDS = {
    "subtotal",
    "tax",
    "total",
}


def _has_blocking_issues(issues):
    return any(
        issue.get("severity") == "error"
        for issue in issues
    )


def _restore_field_types(fields):
    restored = {}

    for field_name, field_value in fields.items():
        if field_value is None:
            restored[field_name] = None
            continue

        if field_name in NUMERIC_FIELDS:
            try:
                restored[field_name] = float(
                    field_value
                )
                continue

            except (
                TypeError,
                ValueError,
            ):
                pass

        restored[field_name] = field_value

    return restored


def _append_duplicate_issue(
    fields,
    document_type,
    issues,
    exclude_document_id=None,
):
    if document_type != "invoice":
        return

    invoice_number = fields.get(
        "invoice_number"
    )

    if not invoice_number:
        return

    if invoice_number_exists(
        invoice_number,
        exclude_document_id=(
            exclude_document_id
        ),
    ):
        issues.append(
            {
                "issue_type":
                    "duplicate_invoice",
                "message": (
                    f"Invoice number "
                    f"{invoice_number} "
                    "already exists."
                ),
                "severity":
                    "warning",
            }
        )


def save_processed_document(
    filename,
    raw_ocr_text,
    scan_result,
    review_status=None,
):
    if not isinstance(
        scan_result,
        dict,
    ):
        return None

    document_type = scan_result.get(
        "document_type"
    )

    scan_mode = scan_result.get(
        "scan_mode"
    )

    fields = scan_result.get(
        "fields"
    )

    if not document_type:
        return None

    if not scan_mode:
        return None

    if not isinstance(
        fields,
        dict,
    ):
        return None

    create_tables()

    validation_issues = (
        validate_scan_result(
            fields,
            document_type,
            scan_mode,
        )
    )

    _append_duplicate_issue(
        fields,
        document_type,
        validation_issues,
    )

    if review_status is None:
        if _has_blocking_issues(
            validation_issues
        ):
            review_status = (
                "pending_review"
            )
        else:
            review_status = (
                "approved"
            )

    document_id = save_document(
        filename,
        document_type,
        scan_mode,
        raw_ocr_text,
        review_status=review_status,
    )

    save_extracted_fields(
        document_id,
        fields,
    )

    save_validation_issues(
        document_id,
        validation_issues,
    )

    return {
        "document_id":
            document_id,
        "validation_issues":
            validation_issues,
        "review_status":
            review_status,
    }


def approve_reviewed_document(
    document_id,
    edited_fields=None,
    note=None,
):
    create_tables()

    document = get_document(
        document_id
    )

    if document is None:
        return {
            "success": False,
            "error":
                "document_not_found",
        }

    stored_fields = get_document_fields(
        document_id
    )

    fields = _restore_field_types(
        stored_fields
    )

    if isinstance(
        edited_fields,
        dict,
    ):
        for field_name, field_value in (
            edited_fields.items()
        ):
            fields[field_name] = (
                field_value
            )

    fields = _restore_field_types(
        fields
    )

    issues = validate_scan_result(
        fields,
        document["document_type"],
        document["scan_mode"],
    )

    _append_duplicate_issue(
        fields,
        document["document_type"],
        issues,
        exclude_document_id=(
            document_id
        ),
    )

    replace_extracted_fields(
        document_id,
        fields,
    )

    replace_validation_issues(
        document_id,
        issues,
    )

    if _has_blocking_issues(
        issues
    ):
        set_document_review_status(
            document_id,
            "pending_review",
            note=note,
        )

        return {
            "success": False,
            "error":
                "validation_errors_remain",
            "document_id":
                document_id,
            "fields":
                fields,
            "validation_issues":
                issues,
            "review_status":
                "pending_review",
        }

    set_document_review_status(
        document_id,
        "approved",
        note=note,
    )

    return {
        "success": True,
        "error": None,
        "document_id":
            document_id,
        "fields":
            fields,
        "validation_issues":
            issues,
        "review_status":
            "approved",
    }


def reject_reviewed_document(
    document_id,
    note=None,
):
    create_tables()

    document = get_document(
        document_id
    )

    if document is None:
        return {
            "success": False,
            "error":
                "document_not_found",
        }

    updated = (
        set_document_review_status(
            document_id,
            "rejected",
            note=note,
        )
    )

    if not updated:
        return {
            "success": False,
            "error":
                "review_update_failed",
        }

    return {
        "success": True,
        "error": None,
        "document_id":
            document_id,
        "review_status":
            "rejected",
    }