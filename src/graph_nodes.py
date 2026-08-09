from src.state import DocumentState
from src.ocr import extract_text
from src.document_type import detect_document_type
from src.extraction import run_full_scan


from src.extraction import (
    run_full_scan,
    run_partial_scan_from_request,
)

def load_node(state: DocumentState):
    image_path = state.get("image_path")

    if not image_path:
        return {
            "error": "Missing image path."
        }

    return {
        "image_path": image_path
    }


def ocr_node(state: DocumentState):
    image_path = state.get("image_path")

    if not image_path:
        return {
            "error": "Cannot run OCR without image path."
        }

    ocr_result = extract_text(image_path)

    if ocr_result is None:
        return {
            "error": "OCR failed."
        }

    return {
        "raw_ocr_text": ocr_result["raw_text"]
    }


def document_type_node(state: DocumentState):
    raw_ocr_text = state.get("raw_ocr_text")

    if not raw_ocr_text:
        return {
            "error": "Cannot detect document type without OCR text."
        }

    document_type = detect_document_type(raw_ocr_text)

    return {
        "document_type": document_type
    }


def scan_mode_router(state: DocumentState):
    scan_mode = state.get("scan_mode")

    if scan_mode == "full":
        return "full"

    if scan_mode == "partial":
        return "partial"

    if scan_mode == "quick":
        return "quick"

    return "error"

def full_scan_node(state: DocumentState):
    raw_ocr_text = state.get("raw_ocr_text")
    document_type = state.get("document_type")

    if not raw_ocr_text or not document_type:
        return {
            "error": "Missing data for full scan."
        }

    scan_result = run_full_scan(
        raw_ocr_text,
        document_type,
    )

    if scan_result is None:
        return {
            "error": "Full scan extraction failed."
        }

    return {
        "scan_result": scan_result
    }

def partial_scan_node(state: DocumentState):
    raw_ocr_text = state.get("raw_ocr_text")
    document_type = state.get("document_type")
    user_request = state.get("user_request")

    if not raw_ocr_text or not document_type or not user_request:
        return {
            "error": "Missing data for partial scan."
        }

    scan_result = run_partial_scan_from_request(
        raw_ocr_text,
        document_type,
        user_request,
    )

    if scan_result is None:
        return {
            "error": "Partial scan extraction failed."
        }

    return {
        "scan_result": scan_result
    }