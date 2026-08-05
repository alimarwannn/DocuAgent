from src.database import (
    create_tables,
    save_document,
    save_extracted_fields,
    save_validation_issues,
)
from src.validation import validate_document


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

    if not document_type or not scan_mode:
        return None

    if not isinstance(fields, dict):
        return None

    create_tables()

    issues = validate_document(
        fields,
        document_type,
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
        issues,
    )

    return {
        "document_id": document_id,
        "validation_issues": issues,
    }