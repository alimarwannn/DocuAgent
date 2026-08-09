from src.graph import build_document_graph

graph = build_document_graph()

initial_state = {
    "image_path": "samples/receipt_1.jpg",
    "scan_mode": "full",
}

result = graph.invoke(initial_state)

assert result is not None
assert "raw_ocr_text" in result
assert "document_type" in result
assert "scan_result" in result
assert "validation_issues" in result
assert "document_id" in result

print("Full LangGraph run passed.")
print("Document type:", result["document_type"])
print("Document ID:", result["document_id"])
print("Validation issues:", result["validation_issues"])