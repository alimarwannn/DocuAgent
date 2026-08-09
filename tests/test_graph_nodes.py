from src.graph_nodes import load_node, ocr_node

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