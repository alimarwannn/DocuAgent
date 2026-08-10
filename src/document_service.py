from src.database import (
    create_tables,
    invoice_number_exists,
    save_document,
    save_extracted_fields,
    save_validation_issues,
)

from src.validation import validate_scan_result


def save_processed_document(
    filename,
    raw_ocr_text,
    scan_result,
):
    if not isinstance(scan_result, dict):
        return None

    document_type = scan_result.get("document_type")
    scan_mode = scan_result.get("scan_mode")
    fields = scan_result.get("fields")

    if not document_type:
        return None

    if not scan_mode:
        return None

    if not isinstance(fields, dict):
        return None

    create_tables()

    validation_issues = validate_scan_result(
        fields,
        document_type,
        scan_mode,
    )

    if document_type == "invoice":
        invoice_number = fields.get("invoice_number")

        if (
            invoice_number
            and invoice_number_exists(invoice_number)
        ):
            validation_issues.append(
                {
                    "issue_type": "duplicate_invoice",
                    "message": (
                        f"Invoice number {invoice_number} "
                        "already exists."
                    ),
                    "severity": "warning",
                }
            )

    document_id = save_document(
        filename,
        document_type,
        scan_mode,
        raw_ocr_text,
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
        "document_id": document_id,
        "validation_issues": validation_issues,
    }