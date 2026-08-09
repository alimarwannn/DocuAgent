from src.graph_nodes import (
    load_node,
    ocr_node,
    document_type_node,
    scan_mode_router,
)

valid_state = {
    "image_path": "samples/receipt_1.jpg"
}

missing_state = {}

valid_result = load_node(valid_state)
missing_result = load_node(missing_state)

assert valid_result["image_path"] == "samples/receipt_1.jpg"
assert missing_result["error"] == "Missing image path."

print("Load node tests passed.")

ocr_state = {
    "image_path": "samples/receipt_1.jpg"
}

ocr_result = ocr_node(ocr_state)

assert "raw_ocr_text" in ocr_result
assert isinstance(ocr_result["raw_ocr_text"], str)
assert len(ocr_result["raw_ocr_text"]) > 0

print("OCR node test passed.")

type_state = {
    "raw_ocr_text": "TAX INVOICE Invoice No: INV-123"
}

type_result = document_type_node(type_state)

assert type_result["document_type"] == "invoice"

missing_type_result = document_type_node({})

assert missing_type_result["error"] == (
    "Cannot detect document type without OCR text."
)

print("Document type node tests passed.")

assert scan_mode_router({"scan_mode": "full"}) == "full"
assert scan_mode_router({"scan_mode": "partial"}) == "partial"
assert scan_mode_router({"scan_mode": "quick"}) == "quick"
assert scan_mode_router({"scan_mode": "invalid"}) == "error"
assert scan_mode_router({}) == "error"

print("Scan mode router tests passed.")