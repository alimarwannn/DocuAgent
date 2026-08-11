import json
import re

from datetime import (
    date,
    timedelta,
)

from src.groq_client import ask_groq


ALLOWED_TOOLS = {
    "list_documents",
    "filter_documents_by_type",
    "filter_documents_by_date",
    "filter_documents_by_party",
    "find_document_by_number",
    "filter_documents_by_amount",
    "total_spend",
    "total_tax",
    "average_document_value",
    "highest_value_documents",
    "supplier_summary",
    "invalid_documents",
    "duplicate_invoices",
    "detect_contradictions",
}


def _selection(
    tool_name,
    arguments=None,
    reason="",
):
    return {
        "tool_name":
            tool_name,
        "arguments":
            arguments or {},
        "reason":
            reason,
        "error":
            None,
    }


def _iso(value):
    return value.isoformat()


def _relative_date_range(
    question,
):
    today = date.today()

    if "today" in question:
        value = _iso(today)

        return (
            value,
            value,
        )

    if "yesterday" in question:
        value = _iso(
            today
            - timedelta(days=1)
        )

        return (
            value,
            value,
        )

    if "this week" in question:
        start = (
            today
            - timedelta(
                days=today.weekday()
            )
        )

        return (
            _iso(start),
            _iso(today),
        )

    if "last week" in question:
        this_week_start = (
            today
            - timedelta(
                days=today.weekday()
            )
        )

        end = (
            this_week_start
            - timedelta(days=1)
        )

        start = (
            end
            - timedelta(days=6)
        )

        return (
            _iso(start),
            _iso(end),
        )

    if "this month" in question:
        start = today.replace(
            day=1
        )

        return (
            _iso(start),
            _iso(today),
        )

    if "last month" in question:
        this_month_start = (
            today.replace(day=1)
        )

        end = (
            this_month_start
            - timedelta(days=1)
        )

        start = end.replace(
            day=1
        )

        return (
            _iso(start),
            _iso(end),
        )

    return None


def _exact_date_range(
    question,
):
    dates = re.findall(
        r"\b\d{4}-\d{2}-\d{2}\b",
        question,
    )

    if len(dates) >= 2:
        return (
            dates[0],
            dates[1],
        )

    if len(dates) == 1:
        return (
            dates[0],
            dates[0],
        )

    return None


def _date_range(
    question,
):
    return (
        _exact_date_range(
            question
        )
        or _relative_date_range(
            question
        )
    )


def _extract_document_number(
    original_question,
):
    pattern = re.compile(
        r"""
        \b
        (?:invoice|receipt)
        \s*
        (?:
            number|
            no\.?
        )?
        \s*
        [:#-]?
        \s*
        (
            [A-Za-z0-9]
            [A-Za-z0-9_\-/]*
            -
            [A-Za-z0-9_\-/]+
            |
            [A-Za-z]*\d[A-Za-z0-9_\-/]*
        )
        """,
        re.IGNORECASE
        | re.VERBOSE,
    )

    match = pattern.search(
        original_question
    )

    if match:
        return match.group(1)

    return None


def _extract_limit(question):
    patterns = [
        r"\btop\s+(\d+)\b",
        r"\b(\d+)\s+highest\b",
        r"\b(\d+)\s+largest\b",
        r"\b(\d+)\s+most expensive\b",
    ]

    for pattern in patterns:
        match = re.search(
            pattern,
            question,
        )

        if match:
            return int(
                match.group(1)
            )

    return 5


def _extract_amount_range(
    question,
):
    between = re.search(
        r"""
        \bbetween\s+
        ([0-9]+(?:\.[0-9]+)?)
        \s+(?:and|to)\s+
        ([0-9]+(?:\.[0-9]+)?)
        """,
        question,
        re.VERBOSE,
    )

    if between:
        return {
            "minimum_amount":
                float(
                    between.group(1)
                ),
            "maximum_amount":
                float(
                    between.group(2)
                ),
        }

    above = re.search(
        r"""
        \b
        (?:
            above|
            over|
            greater\s+than|
            more\s+than
        )
        \s+
        ([0-9]+(?:\.[0-9]+)?)
        """,
        question,
        re.VERBOSE,
    )

    if above:
        return {
            "minimum_amount":
                float(
                    above.group(1)
                ),
        }

    below = re.search(
        r"""
        \b
        (?:
            below|
            under|
            less\s+than
        )
        \s+
        ([0-9]+(?:\.[0-9]+)?)
        """,
        question,
        re.VERBOSE,
    )

    if below:
        return {
            "maximum_amount":
                float(
                    below.group(1)
                ),
        }

    return None


def deterministic_tool_selection(
    question,
):
    original = question.strip()
    lowered = original.lower()

    document_number = (
        _extract_document_number(
            original
        )
    )

    if document_number:
        return _selection(
            "find_document_by_number",
            {
                "document_number":
                    document_number,
            },
            "Specific document number detected.",
        )

    if (
        "duplicate" in lowered
        or (
            "repeated" in lowered
            and "invoice" in lowered
        )
    ):
        return _selection(
            "duplicate_invoices",
            reason=(
                "Duplicate invoice question detected."
            ),
        )

    if any(
        phrase in lowered
        for phrase in [
            "contradiction",
            "contradictions",
            "conflicting",
            "conflict",
            "inconsistent",
            "inconsistency",
        ]
    ):
        return _selection(
            "detect_contradictions",
            reason=(
                "Contradiction question detected."
            ),
        )

    if any(
        phrase in lowered
        for phrase in [
            "validation problem",
            "validation problems",
            "validation issue",
            "validation issues",
            "invalid document",
            "invalid documents",
            "documents with problems",
        ]
    ):
        return _selection(
            "invalid_documents",
            reason=(
                "Validation issue question detected."
            ),
        )

    date_range = _date_range(
        lowered
    )

    if (
        "tax" in lowered
        and any(
            phrase in lowered
            for phrase in [
                "total",
                "how much",
                "sum",
            ]
        )
    ):
        arguments = {}

        if date_range:
            arguments = {
                "start_date":
                    date_range[0],
                "end_date":
                    date_range[1],
            }

        return _selection(
            "total_tax",
            arguments,
            "Total tax question detected.",
        )

    if any(
        phrase in lowered
        for phrase in [
            "how much did i spend",
            "how much have i spent",
            "total spend",
            "total spending",
            "how much was spent",
        ]
    ):
        arguments = {}

        if date_range:
            arguments = {
                "start_date":
                    date_range[0],
                "end_date":
                    date_range[1],
            }

        return _selection(
            "total_spend",
            arguments,
            "Spending question detected.",
        )

    if (
        "average" in lowered
        and any(
            word in lowered
            for word in [
                "invoice",
                "document",
                "value",
                "amount",
            ]
        )
    ):
        arguments = {}

        if date_range:
            arguments = {
                "start_date":
                    date_range[0],
                "end_date":
                    date_range[1],
            }

        return _selection(
            "average_document_value",
            arguments,
            "Average value question detected.",
        )

    if any(
        phrase in lowered
        for phrase in [
            "highest value",
            "highest-value",
            "largest invoice",
            "largest document",
            "most expensive",
            "top invoices",
            "top documents",
        ]
    ):
        return _selection(
            "highest_value_documents",
            {
                "limit":
                    _extract_limit(
                        lowered
                    ),
            },
            "Highest value question detected.",
        )

    if (
        "supplier" in lowered
        or "merchant" in lowered
    ):
        if any(
            phrase in lowered
            for phrase in [
                "most often",
                "most common",
                "summary",
                "appear most",
                "spending by",
                "supplier spending",
            ]
        ):
            return _selection(
                "supplier_summary",
                reason=(
                    "Supplier summary question detected."
                ),
            )

        party_match = re.search(
            r"\b(?:from|by)\s+(.+?)(?:\?|$)",
            original,
            re.IGNORECASE,
        )

        if party_match:
            party = (
                party_match
                .group(1)
                .strip()
                .rstrip(".")
            )

            if party:
                return _selection(
                    "filter_documents_by_party",
                    {
                        "name":
                            party,
                    },
                    "Supplier or merchant filter detected.",
                )

    amount_range = (
        _extract_amount_range(
            lowered
        )
    )

    if amount_range:
        return _selection(
            "filter_documents_by_amount",
            amount_range,
            "Amount filter detected.",
        )

    if date_range and any(
        word in lowered
        for word in [
            "document",
            "documents",
            "invoice",
            "invoices",
            "receipt",
            "receipts",
            "show",
            "list",
        ]
    ):
        return _selection(
            "filter_documents_by_date",
            {
                "start_date":
                    date_range[0],
                "end_date":
                    date_range[1],
            },
            "Date range filter detected.",
        )

    if any(
        phrase in lowered
        for phrase in [
            "all invoices",
            "show invoices",
            "list invoices",
            "my invoices",
        ]
    ):
        return _selection(
            "filter_documents_by_type",
            {
                "document_type":
                    "invoice",
            },
            "Invoice list requested.",
        )

    if any(
        phrase in lowered
        for phrase in [
            "all receipts",
            "show receipts",
            "list receipts",
            "my receipts",
        ]
    ):
        return _selection(
            "filter_documents_by_type",
            {
                "document_type":
                    "receipt",
            },
            "Receipt list requested.",
        )

    if any(
        phrase in lowered
        for phrase in [
            "all documents",
            "show documents",
            "list documents",
            "my documents",
        ]
    ):
        return _selection(
            "list_documents",
            reason=(
                "Document list requested."
            ),
        )

    return None


def parse_json_response(response):
    if not response:
        return None

    cleaned = response.strip()

    cleaned = re.sub(
        r"^```(?:json)?",
        "",
        cleaned,
        flags=re.IGNORECASE,
    )

    cleaned = re.sub(
        r"```$",
        "",
        cleaned,
    )

    cleaned = cleaned.strip()

    try:
        return json.loads(
            cleaned
        )

    except json.JSONDecodeError:
        pass

    start = cleaned.find("{")
    end = cleaned.rfind("}")

    if (
        start == -1
        or end == -1
    ):
        return None

    try:
        return json.loads(
            cleaned[
                start:end + 1
            ]
        )

    except json.JSONDecodeError:
        return None


def build_tool_selection_prompt(
    question,
):
    today = date.today().isoformat()

    return f"""
You are Zaki, the chatbot inside DocuAgent.

Today is {today}.

Select exactly one deterministic Python or SQLite tool.

Do not answer the user's question.
Do not calculate database values.
Do not invent missing information.

Available tools:

list_documents
Arguments: {{}}

filter_documents_by_type
Arguments:
{{
    "document_type": "invoice or receipt"
}}

filter_documents_by_date
Arguments:
{{
    "start_date": "YYYY-MM-DD",
    "end_date": "YYYY-MM-DD"
}}

filter_documents_by_party
Arguments:
{{
    "name": "supplier or merchant name"
}}

find_document_by_number
Arguments:
{{
    "document_number": "number"
}}

filter_documents_by_amount
Arguments:
{{
    "minimum_amount": number or null,
    "maximum_amount": number or null
}}

total_spend
Arguments:
{{
    "start_date": "YYYY-MM-DD or null",
    "end_date": "YYYY-MM-DD or null"
}}

total_tax
Arguments:
{{
    "start_date": "YYYY-MM-DD or null",
    "end_date": "YYYY-MM-DD or null"
}}

average_document_value
Arguments:
{{
    "start_date": "YYYY-MM-DD or null",
    "end_date": "YYYY-MM-DD or null"
}}

highest_value_documents
Arguments:
{{
    "limit": integer
}}

supplier_summary
Arguments: {{}}

invalid_documents
Arguments: {{}}

duplicate_invoices
Arguments: {{}}

detect_contradictions
Arguments: {{}}

Return JSON only:

{{
    "tool_name": "tool name or null",
    "arguments": {{}},
    "reason": "short reason"
}}

User question:
{question}
"""


def select_zaki_tool(question):
    if not isinstance(
        question,
        str,
    ):
        return {
            "tool_name": None,
            "arguments": {},
            "reason":
                "Question must be text.",
            "error":
                "invalid_question",
        }

    question = question.strip()

    if not question:
        return {
            "tool_name": None,
            "arguments": {},
            "reason":
                "Question is empty.",
            "error":
                "empty_question",
        }

    fast_selection = (
        deterministic_tool_selection(
            question
        )
    )

    if fast_selection is not None:
        return fast_selection

    prompt = (
        build_tool_selection_prompt(
            question
        )
    )

    response = ask_groq(
        prompt
    )

    parsed = parse_json_response(
        response
    )

    if not isinstance(
        parsed,
        dict,
    ):
        return {
            "tool_name": None,
            "arguments": {},
            "reason": (
                "Zaki could not understand "
                "the tool selection response."
            ),
            "error":
                "invalid_llm_response",
        }

    tool_name = parsed.get(
        "tool_name"
    )

    arguments = parsed.get(
        "arguments",
        {},
    )

    reason = parsed.get(
        "reason",
        "",
    )

    if tool_name is None:
        return {
            "tool_name": None,
            "arguments": {},
            "reason": (
                reason
                or "No suitable tool was found."
            ),
            "error":
                "unsupported_question",
        }

    if tool_name not in ALLOWED_TOOLS:
        return {
            "tool_name": None,
            "arguments": {},
            "reason": (
                f"Tool '{tool_name}' "
                "is not allowed."
            ),
            "error":
                "invalid_tool",
        }

    if not isinstance(
        arguments,
        dict,
    ):
        arguments = {}

    return {
        "tool_name":
            tool_name,
        "arguments":
            arguments,
        "reason":
            reason,
        "error":
            None,
    }