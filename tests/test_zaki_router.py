from src.zaki_router import select_zaki_tool


tests = [
    (
        "How much did I spend?",
        "total_spend",
    ),
    (
        "What was the total tax?",
        "total_tax",
    ),
    (
        "Show me all invoices.",
        "filter_documents_by_type",
    ),
    (
        "Find invoice PEGIV-1030765.",
        "find_document_by_number",
    ),
    (
        "Show documents above 1000 EGP.",
        "filter_documents_by_amount",
    ),
    (
        "Which documents have validation problems?",
        "invalid_documents",
    ),
    (
        "Are there duplicate invoices?",
        "duplicate_invoices",
    ),
    (
        "Are there contradictions between my documents?",
        "detect_contradictions",
    ),
    (
        "Which suppliers appear most often?",
        "supplier_summary",
    ),
    (
        "Show me the 3 highest value documents.",
        "highest_value_documents",
    ),
]


for question, expected_tool in tests:
    print()
    print("Question:", question)

    result = select_zaki_tool(question)

    print("Selected:", result)

    assert result["error"] is None
    assert result["tool_name"] == expected_tool


empty_result = select_zaki_tool("")

assert empty_result["tool_name"] is None
assert empty_result["error"] == "empty_question"


print()
print("Zaki tool selection tests passed.")