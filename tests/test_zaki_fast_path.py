import src.zaki_chat as zaki_chat
import src.zaki_router as zaki_router

from src.zaki_chat import (
    generate_grounded_answer,
)

from src.zaki_router import (
    select_zaki_tool,
)


def fail_if_groq_is_called(*args, **kwargs):
    raise AssertionError(
        "Groq should not be called "
        "for this fast-path test."
    )


zaki_router.ask_groq = (
    fail_if_groq_is_called
)

zaki_chat.ask_groq = (
    fail_if_groq_is_called
)


tests = [
    (
        "How much did I spend?",
        "total_spend",
    ),
    (
        "How much did I spend last week?",
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
        "Show documents above 1000 EGP.",
        "filter_documents_by_amount",
    ),
    (
        "Are there duplicate invoices?",
        "duplicate_invoices",
    ),
    (
        "Are there contradictions?",
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
    result = select_zaki_tool(
        question
    )

    assert (
        result["error"]
        is None
    )

    assert (
        result["tool_name"]
        == expected_tool
    )


last_week = select_zaki_tool(
    "How much did I spend last week?"
)

assert (
    last_week["arguments"].get(
        "start_date"
    )
    is not None
)

assert (
    last_week["arguments"].get(
        "end_date"
    )
    is not None
)


answer = generate_grounded_answer(
    "How much did I spend?",
    {
        "success": True,
        "tool_name":
            "total_spend",
        "arguments": {},
        "result": {
            "total": 1140,
            "document_count": 1,
            "documents": [],
        },
        "error": None,
    },
)

assert "1,140" in answer


answer = generate_grounded_answer(
    "Are there duplicate invoices?",
    {
        "success": True,
        "tool_name":
            "duplicate_invoices",
        "arguments": {},
        "result": [],
        "error": None,
    },
)

assert "duplicate" in (
    answer.lower()
)


print(
    "Zaki fast-path tests passed."
)