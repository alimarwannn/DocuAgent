from src.state import DocumentState

from src.ocr import extract_text

from src.document_type import (
    detect_document_type,
)

from src.extraction import (
    run_full_scan,
    run_partial_scan_from_request,
    run_quick_scan,
)

from src.normalization import (
    normalize_fields,
)

from src.validation import (
    validate_scan_result,
)

from src.document_service import (
    save_processed_document,
)


SUPPORTED_DOCUMENT_TYPES = {
    "invoice",
    "receipt",
}


def load_node(state: DocumentState):
    image_path = state.get(
        "image_path"
    )

    if not image_path:
        return {
            "error":
                "Missing image path."
        }

    return {
        "image_path":
            image_path
    }


def ocr_node(state: DocumentState):
    image_path = state.get(
        "image_path"
    )

    if not image_path:
        return {
            "error":
                "Cannot run OCR without image path."
        }

    ocr_result = extract_text(
        image_path
    )

    if ocr_result is None:
        return {
            "error":
                "OCR failed."
        }

    raw_text = (
        ocr_result
        .get(
            "raw_text",
            "",
        )
        .strip()
    )

    if not raw_text:
        return {
            "error":
                "OCR returned no readable text."
        }

    return {
        "raw_ocr_text":
            raw_text
    }


def document_type_node(
    state: DocumentState,
):
    override = state.get(
        "document_type_override"
    )

    if override in (
        SUPPORTED_DOCUMENT_TYPES
    ):
        return {
            "document_type":
                override
        }

    raw_ocr_text = state.get(
        "raw_ocr_text"
    )

    if not raw_ocr_text:
        return {
            "error": (
                "Cannot detect document type "
                "without OCR text."
            )
        }

    document_type = (
        detect_document_type(
            raw_ocr_text
        )
    )

    if (
        document_type
        not in SUPPORTED_DOCUMENT_TYPES
    ):
        return {
            "document_type":
                "unknown",
            "error":
                "Unsupported document type.",
        }

    return {
        "document_type":
            document_type
    }


def scan_mode_router(
    state: DocumentState,
):
    if state.get("error"):
        return "error"

    scan_mode = state.get(
        "scan_mode"
    )

    if scan_mode == "full":
        return "full"

    if scan_mode == "partial":
        return "partial"

    if scan_mode == "quick":
        return "quick"

    return "error"


def error_router(
    state: DocumentState,
):
    if state.get("error"):
        return "error"

    return "continue"


def full_scan_node(
    state: DocumentState,
):
    raw_ocr_text = state.get(
        "raw_ocr_text"
    )

    document_type = state.get(
        "document_type"
    )

    if (
        not raw_ocr_text
        or not document_type
    ):
        return {
            "error":
                "Missing data for full scan."
        }

    try:
        scan_result = run_full_scan(
            raw_ocr_text,
            document_type,
        )

    except Exception as error:
        return {
            "error": (
                "Full scan extraction failed: "
                f"{error}"
            )
        }

    if scan_result is None:
        return {
            "error":
                "Full scan extraction failed."
        }

    return {
        "scan_result":
            scan_result
    }


def partial_scan_node(
    state: DocumentState,
):
    raw_ocr_text = state.get(
        "raw_ocr_text"
    )

    document_type = state.get(
        "document_type"
    )

    user_request = state.get(
        "user_request"
    )

    if (
        not raw_ocr_text
        or not document_type
        or not user_request
    ):
        return {
            "error":
                "Missing data for partial scan."
        }

    try:
        scan_result = (
            run_partial_scan_from_request(
                raw_ocr_text,
                document_type,
                user_request,
            )
        )

    except Exception as error:
        return {
            "error": (
                "Partial scan extraction failed: "
                f"{error}"
            )
        }

    if scan_result is None:
        return {
            "error":
                "Partial scan extraction failed."
        }

    return {
        "scan_result":
            scan_result
    }


def quick_scan_node(
    state: DocumentState,
):
    raw_ocr_text = state.get(
        "raw_ocr_text"
    )

    document_type = state.get(
        "document_type"
    )

    if (
        not raw_ocr_text
        or not document_type
    ):
        return {
            "error":
                "Missing data for quick scan."
        }

    try:
        scan_result = run_quick_scan(
            raw_ocr_text,
            document_type,
        )

    except Exception as error:
        return {
            "error": (
                "Quick scan failed: "
                f"{error}"
            )
        }

    if scan_result is None:
        return {
            "error":
                "Quick scan failed."
        }

    return {
        "scan_result":
            scan_result
    }


def normalization_node(
    state: DocumentState,
):
    scan_result = state.get(
        "scan_result"
    )

    if not isinstance(
        scan_result,
        dict,
    ):
        return {
            "error": (
                "Missing scan result "
                "for normalization."
            )
        }

    fields = scan_result.get(
        "fields"
    )

    if not isinstance(
        fields,
        dict,
    ):
        return {
            "error": (
                "Invalid fields "
                "for normalization."
            )
        }

    normalized_result = (
        scan_result.copy()
    )

    normalized_result["fields"] = (
        normalize_fields(
            fields,
            state.get(
                "raw_ocr_text"
            ),
        )
    )

    return {
        "scan_result":
            normalized_result
    }


def validation_node(
    state: DocumentState,
):
    scan_result = state.get(
        "scan_result"
    )

    if not isinstance(
        scan_result,
        dict,
    ):
        return {
            "error": (
                "Missing scan result "
                "for validation."
            )
        }

    document_type = (
        scan_result.get(
            "document_type"
        )
    )

    scan_mode = (
        scan_result.get(
            "scan_mode"
        )
    )

    fields = scan_result.get(
        "fields"
    )

    if (
        not document_type
        or not scan_mode
        or not isinstance(
            fields,
            dict,
        )
    ):
        return {
            "error": (
                "Invalid scan result "
                "for validation."
            )
        }

    validation_issues = (
        validate_scan_result(
            fields,
            document_type,
            scan_mode,
        )
    )

    return {
        "validation_issues":
            validation_issues
    }


def review_router(
    state: DocumentState,
):
    if state.get("error"):
        return "error"

    issues = state.get(
        "validation_issues",
        [],
    )

    for issue in issues:
        if (
            issue.get("severity")
            == "error"
        ):
            return "review"

    return "save"


def human_review_node(
    state: DocumentState,
):
    image_path = state.get(
        "image_path"
    )

    raw_ocr_text = state.get(
        "raw_ocr_text"
    )

    scan_result = state.get(
        "scan_result"
    )

    if (
        not image_path
        or not raw_ocr_text
        or not isinstance(
            scan_result,
            dict,
        )
    ):
        return {
            "needs_human_review":
                True,
            "error": (
                "Could not save document "
                "for review."
            ),
        }

    saved_result = (
        save_processed_document(
            filename=image_path,
            raw_ocr_text=raw_ocr_text,
            scan_result=scan_result,
            review_status=(
                "pending_review"
            ),
        )
    )

    if saved_result is None:
        return {
            "needs_human_review":
                True,
            "error": (
                "Could not save document "
                "for review."
            ),
        }

    return {
        "document_id":
            saved_result[
                "document_id"
            ],
        "validation_issues":
            saved_result[
                "validation_issues"
            ],
        "needs_human_review":
            True,
    }


def save_node(
    state: DocumentState,
):
    image_path = state.get(
        "image_path"
    )

    raw_ocr_text = state.get(
        "raw_ocr_text"
    )

    scan_result = state.get(
        "scan_result"
    )

    if (
        not image_path
        or not raw_ocr_text
        or not isinstance(
            scan_result,
            dict,
        )
    ):
        return {
            "error":
                "Missing data for saving."
        }

    saved_result = (
        save_processed_document(
            filename=image_path,
            raw_ocr_text=raw_ocr_text,
            scan_result=scan_result,
            review_status=(
                "approved"
            ),
        )
    )

    if saved_result is None:
        return {
            "error":
                "Saving document failed."
        }

    return {
        "document_id":
            saved_result[
                "document_id"
            ],
        "validation_issues":
            saved_result[
                "validation_issues"
            ],
        "needs_human_review":
            False,
    }