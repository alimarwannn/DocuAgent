from src.graph import build_document_graph


graph = build_document_graph()

initial_state = {
    "image_path": "samples/receipt_1.jpg",
    "scan_mode": "full",
}

result = graph.invoke(initial_state)

print("FULL RESULT:", result)

assert result is not None
assert "raw_ocr_text" in result
assert "document_type" in result

if result.get("error"):
    raise AssertionError(
        f"Graph failed: {result['error']}"
    )

assert "scan_result" in result

fields = result["scan_result"]["fields"]

assert fields["date"] == "2019-01-15"
assert fields["currency"] == "SAR"

issue_types = [
    issue["issue_type"]
    for issue in result.get(
        "validation_issues",
        [],
    )
]

assert "invalid_date" not in issue_types
assert "invalid_currency" not in issue_types

if result.get("needs_human_review"):
    print("Document sent to human review.")
else:
    assert "document_id" in result
    print(
        "Document ID:",
        result["document_id"],
    )

print(
    "Document type:",
    result["document_type"],
)

print(
    "Validation issues:",
    result.get(
        "validation_issues",
        [],
    ),
)

print(
    "Scan result:",
    result["scan_result"],
)

print("Full LangGraph run passed.")