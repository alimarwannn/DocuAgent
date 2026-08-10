import json
import re

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
        return json.loads(cleaned)
    except json.JSONDecodeError:
        pass

    start = cleaned.find("{")
    end = cleaned.rfind("}")

    if start == -1 or end == -1:
        return None

    try:
        return json.loads(cleaned[start:end + 1])
    except json.JSONDecodeError:
        return None


def build_tool_selection_prompt(question):
    return f"""
You are Zaki, the chatbot inside DocuAgent.

Your job is ONLY to understand the user's question and select one deterministic Python/SQLite tool.

Do not answer the question.
Do not calculate totals yourself.
Do not invent database values.

Available tools:

list_documents
Use for:
- show all documents
- list saved documents
Arguments:
{{}}

filter_documents_by_type
Use for:
- show invoices
- show receipts
Arguments:
{{
    "document_type": "invoice or receipt"
}}

filter_documents_by_date
Use for:
- documents between two exact dates
Arguments:
{{
    "start_date": "YYYY-MM-DD",
    "end_date": "YYYY-MM-DD"
}}

filter_documents_by_party
Use for:
- documents from a supplier or merchant
Arguments:
{{
    "name": "supplier or merchant name"
}}

find_document_by_number
Use for:
- find a specific invoice or receipt number
Arguments:
{{
    "document_number": "number"
}}

filter_documents_by_amount
Use for:
- documents above, below or between amounts
Arguments:
{{
    "minimum_amount": number or null,
    "maximum_amount": number or null
}}

total_spend
Use for:
- total spend
- how much was spent
Arguments:
{{
    "start_date": "YYYY-MM-DD or null",
    "end_date": "YYYY-MM-DD or null"
}}

total_tax
Use for:
- total tax
Arguments:
{{
    "start_date": "YYYY-MM-DD or null",
    "end_date": "YYYY-MM-DD or null"
}}

average_document_value
Use for:
- average invoice value
- average document value
Arguments:
{{
    "start_date": "YYYY-MM-DD or null",
    "end_date": "YYYY-MM-DD or null"
}}

highest_value_documents
Use for:
- highest invoices
- largest documents
- most expensive documents
Arguments:
{{
    "limit": integer
}}

supplier_summary
Use for:
- most common suppliers
- supplier summary
- supplier spending
Arguments:
{{}}

invalid_documents
Use for:
- documents with validation problems
- invalid documents
Arguments:
{{}}

duplicate_invoices
Use for:
- duplicate invoices
- repeated invoice numbers
Arguments:
{{}}

detect_contradictions
Use for:
- contradictions
- conflicting invoices
- inconsistent totals, suppliers or dates
Arguments:
{{}}

Important:
- Return JSON only.
- Return exactly one tool.
- Never invent missing arguments.
- Use null when an optional value is unknown.
- If the question cannot be handled, use tool_name = null.

Required response format:

{{
    "tool_name": "tool name or null",
    "arguments": {{}},
    "reason": "short explanation"
}}

User question:
{question}
"""


def select_zaki_tool(question):
    if not isinstance(question, str):
        return {
            "tool_name": None,
            "arguments": {},
            "reason": "Question must be text.",
            "error": "invalid_question",
        }

    question = question.strip()

    if not question:
        return {
            "tool_name": None,
            "arguments": {},
            "reason": "Question is empty.",
            "error": "empty_question",
        }

    prompt = build_tool_selection_prompt(question)

    response = ask_groq(prompt)

    parsed = parse_json_response(response)

    if not isinstance(parsed, dict):
        return {
            "tool_name": None,
            "arguments": {},
            "reason": "Zaki could not understand the tool selection response.",
            "error": "invalid_llm_response",
        }

    tool_name = parsed.get("tool_name")
    arguments = parsed.get("arguments", {})
    reason = parsed.get("reason", "")

    if tool_name is None:
        return {
            "tool_name": None,
            "arguments": {},
            "reason": reason or "No suitable tool was found.",
            "error": "unsupported_question",
        }

    if tool_name not in ALLOWED_TOOLS:
        return {
            "tool_name": None,
            "arguments": {},
            "reason": f"Tool '{tool_name}' is not allowed.",
            "error": "invalid_tool",
        }

    if not isinstance(arguments, dict):
        arguments = {}

    return {
        "tool_name": tool_name,
        "arguments": arguments,
        "reason": reason,
        "error": None,
    }