from src.graph import (
    build_document_graph,
)


graph = build_document_graph()


result = graph.invoke(
    {
        "image_path":
            "samples/receipt_1.jpg",

        "scan_mode":
            "full",

        "error":
            None,
    }
)


print(
    "FULL RESULT:",
    result,
)


assert (
    result["document_type"]
    == "receipt"
)


scan_result = (
    result["scan_result"]
)

assert (
    scan_result["document_type"]
    == "receipt"
)

assert (
    scan_result["scan_mode"]
    == "full"
)


fields = (
    scan_result["fields"]
)


assert (
    fields["merchant_name"]
    == "OJC MARKETING SDN BHD"
)


assert (
    fields["receipt_number"]
    == "PEGIV-1030765"
)


assert (
    fields["date"]
    == "2019-01-15"
)


assert (
    float(
        fields["subtotal"]
    )
    == 193.0
)


assert (
    float(
        fields["tax"]
    )
    == 0.0
)


assert (
    float(
        fields["total"]
    )
    == 193.0
)


# The OCR does not explicitly show a
# supported currency code or symbol.
# DocuAgent must not invent one.
assert (
    fields["currency"]
    is None
)


# Currency is unknown, so this full scan
# should safely require human review.
assert (
    result[
        "needs_human_review"
    ]
    is True
)


issues = (
    result.get(
        "validation_issues",
        [],
    )
)


assert any(
    issue[
        "issue_type"
    ]
    == "missing_currency"

    for issue
    in issues
)


print(
    "Full graph grounding test passed."
)