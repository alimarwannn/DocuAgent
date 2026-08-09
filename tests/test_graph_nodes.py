from src.graph_nodes import (
    load_node,
    ocr_node,
    document_type_node,
    scan_mode_router,
    full_scan_node,
    partial_scan_node,
    quick_scan_node,
    validation_node,
    save_node,
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

full_scan_state = {
    "raw_ocr_text": """
    TAX INVOICE
    Supplier: Vodafone Egypt
    Invoice No: GRAPH-001
    Date: 2026-08-09
    Subtotal: 1000
    Tax: 140
    Total: 1140 EGP
    """,
    "document_type": "invoice",
}

full_scan_result = full_scan_node(full_scan_state)

assert "scan_result" in full_scan_result
assert full_scan_result["scan_result"]["document_type"] == "invoice"
assert full_scan_result["scan_result"]["scan_mode"] == "full"

print("Full scan node tests passed.")

partial_scan_state = {
    "raw_ocr_text": """
    TAX INVOICE
    Invoice No: GRAPH-002
    Total: 500 EGP
    """,
    "document_type": "invoice",
    "user_request": "Extract the invoice number and total.",
}

partial_scan_result = partial_scan_node(partial_scan_state)

assert "scan_result" in partial_scan_result
assert partial_scan_result["scan_result"]["document_type"] == "invoice"
assert partial_scan_result["scan_result"]["scan_mode"] == "partial"

print("Partial scan node tests passed.")

quick_scan_state = {
    "raw_ocr_text": """
    TAX INVOICE
    Invoice Number: GRAPH-003
    Date: 2026-08-09
    Total: 700 EGP
    """,
    "document_type": "invoice",
}

quick_scan_result = quick_scan_node(quick_scan_state)

assert "scan_result" in quick_scan_result
assert quick_scan_result["scan_result"]["document_type"] == "invoice"
assert quick_scan_result["scan_result"]["scan_mode"] == "quick"

print("Quick scan node tests passed.")

validation_state = {
    "scan_result": {
        "document_type": "invoice",
        "scan_mode": "full",
        "fields": {
            "supplier_name": "Vodafone Egypt",
            "invoice_number": "GRAPH-004",
            "date": "2026-08-09",
            "customer": None,
            "subtotal": 1000,
            "tax": 140,
            "total": 1200,
            "currency": "EGP",
        },
    }
}

validation_result = validation_node(validation_state)

assert "validation_issues" in validation_result
assert len(validation_result["validation_issues"]) == 1
assert validation_result["validation_issues"][0]["issue_type"] == "total_mismatch"

print("Validation node tests passed.")

save_state = {
    "image_path": "samples/graph_save_test.jpg",
    "raw_ocr_text": "TAX INVOICE Invoice No: GRAPH-SAVE-001",
    "scan_result": {
        "document_type": "invoice",
        "scan_mode": "full",
        "fields": {
            "supplier_name": "Vodafone Egypt",
            "invoice_number": "GRAPH-SAVE-001",
            "date": "2026-08-09",
            "customer": None,
            "subtotal": 1000,
            "tax": 140,
            "total": 1140,
            "currency": "EGP",
        },
    },
}

save_result = save_node(save_state)

assert "document_id" in save_result
assert isinstance(save_result["document_id"], int)
assert save_result["validation_issues"] == []

missing_save_result = save_node({})

assert missing_save_result["error"] == "Missing data for saving."

print("Save node tests passed.")