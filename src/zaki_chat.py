import json

from src.groq_client import ask_groq

from src.zaki_executor import (
    execute_zaki_tool,
)

from src.zaki_router import (
    select_zaki_tool,
)


def _number(value):
    try:
        number = float(value)

    except (
        TypeError,
        ValueError,
    ):
        return str(value)

    if number.is_integer():
        return f"{int(number):,}"

    return f"{number:,.2f}"


def _currency_amount(
    currency,
    value,
):
    if currency in (None, ""):
        return _number(value)

    return f"{currency} {_number(value)}"


def _grouped_currency_totals(values):
    return "; ".join(
        _currency_amount(currency, total)
        for currency, total in values.items()
    )


def _references(documents):
    if not documents:
        return ""

    references = [
        f"#{document['id']}"
        for document in documents[:5]
        if document.get("id")
        is not None
    ]

    if not references:
        return ""

    result = ", ".join(
        references
    )

    if len(documents) > 5:
        result += (
            f" and "
            f"{len(documents) - 5} more"
        )

    return result


def format_deterministic_answer(
    question,
    tool_name,
    result,
):
    if tool_name == "list_documents":
        count = len(result)

        if count == 0:
            return (
                "You don't have any saved "
                "documents yet."
            )

        return (
            f"You have {count} saved "
            f"document{'s' if count != 1 else ''}."
        )

    if tool_name in {
        "filter_documents_by_type",
        "filter_documents_by_date",
        "filter_documents_by_party",
        "filter_documents_by_amount",
    }:
        count = len(result)

        if count == 0:
            return (
                "I couldn't find any matching "
                "documents."
            )

        refs = _references(
            result
        )

        answer = (
            f"I found {count} matching "
            f"document{'s' if count != 1 else ''}."
        )

        if refs:
            answer += (
                f" References: {refs}."
            )

        return answer

    if tool_name == (
        "find_document_by_number"
    ):
        if not result:
            return (
                "I couldn't find a document "
                "with that number."
            )

        refs = _references(
            result
        )

        if len(result) == 1:
            return (
                f"I found it in document "
                f"{refs}."
            )

        return (
            f"I found {len(result)} matching "
            f"documents: {refs}."
        )

    if tool_name == "total_spend":
        count = result.get(
            "document_count",
            0,
        )

        totals_by_currency = result.get(
            "totals_by_currency",
            {},
        )

        if count == 0:
            return (
                "I couldn't find any approved "
                "documents for that spending question."
            )

        if len(totals_by_currency) > 1:
            return (
                f"Across {count} approved "
                f"document{'s' if count != 1 else ''}, "
                f"spend is grouped by currency: "
                f"{_grouped_currency_totals(totals_by_currency)}."
            )

        currency = result.get(
            "currency"
        )
        total = result.get(
            "total",
            0,
        )

        return (
            f"The total across {count} approved "
            f"document{'s' if count != 1 else ''} "
            f"is {_currency_amount(currency, total)}."
        )

    if tool_name == "total_tax":
        count = result.get(
            "document_count",
            0,
        )

        totals_by_currency = result.get(
            "totals_by_currency",
            {},
        )

        if count == 0:
            return (
                "I couldn't find any approved "
                "documents for that tax question."
            )

        if len(totals_by_currency) > 1:
            return (
                f"Across {count} approved "
                f"document{'s' if count != 1 else ''}, "
                f"tax is grouped by currency: "
                f"{_grouped_currency_totals(totals_by_currency)}."
            )

        currency = result.get(
            "currency"
        )
        total_tax = result.get(
            "total_tax",
            0,
        )

        return (
            f"The total tax across {count} approved "
            f"document{'s' if count != 1 else ''} "
            f"is {_currency_amount(currency, total_tax)}."
        )

    if tool_name == (
        "average_document_value"
    ):
        count = result.get(
            "document_count",
            0,
        )

        if count == 0:
            return (
                "There are no matching "
                "documents to average."
            )

        averages_by_currency = result.get(
            "averages_by_currency",
            {},
        )

        if len(averages_by_currency) > 1:
            return (
                f"Across {count} approved documents, "
                f"the average value is grouped by currency: "
                f"{_grouped_currency_totals(averages_by_currency)}."
            )

        currency = result.get(
            "currency"
        )
        average = result.get(
            "average",
            0,
        )

        return (
            f"The average value across {count} approved "
            f"document{'s' if count != 1 else ''} "
            f"is {_currency_amount(currency, average)}."
        )

    if tool_name == (
        "highest_value_documents"
    ):
        if not result:
            return (
                "I couldn't find any documents "
                "with a recorded total."
            )

        lines = []

        for document in result:
            document_id = (
                document.get("id")
            )

            total = document.get(
                "total",
                0,
            )

            currency = document.get(
                "currency"
            )

            lines.append(
                f"#{document_id}: {_currency_amount(currency, total)}"
            )

        return (
            "The highest-value approved documents are "
            + "; ".join(lines)
            + "."
        )

    if tool_name == "supplier_summary":
        if not result:
            return (
                "I couldn't find any supplier "
                "information."
            )

        top = result[0]

        supplier = top.get(
            "supplier",
            "Unknown supplier",
        )

        count = top.get(
            "document_count",
            0,
        )

        return (
            f"{supplier} appears most often "
            f"in approved documents with {count} "
            f"document{'s' if count != 1 else ''}."
        )

    if tool_name == "invalid_documents":
        if not result:
            return (
                "I couldn't find any documents "
                "with validation problems."
            )

        refs = _references(
            result
        )

        return (
            f"{len(result)} document"
            f"{'s' if len(result) != 1 else ''} "
            f"need attention. "
            f"References: {refs}."
        )

    if tool_name == "duplicate_invoices":
        if not result:
            return (
                "I couldn't find any duplicate "
                "invoice numbers."
            )

        summaries = []

        for duplicate in result[:5]:
            summaries.append(
                (
                    f"{duplicate['invoice_number']} "
                    f"({duplicate['occurrence_count']} times)"
                )
            )

        answer = (
            "I found duplicate invoice numbers: "
            + ", ".join(
                summaries
            )
            + "."
        )

        if len(result) > 5:
            answer += (
                f" There are "
                f"{len(result) - 5} more."
            )

        return answer

    if tool_name == (
        "detect_contradictions"
    ):
        if not result:
            return (
                "I couldn't find any contradictions "
                "between the saved invoices."
            )

        invoice_numbers = []

        for contradiction in result:
            invoice_number = (
                contradiction.get(
                    "invoice_number"
                )
            )

            if (
                invoice_number
                and invoice_number
                not in invoice_numbers
            ):
                invoice_numbers.append(
                    invoice_number
                )

        preview = ", ".join(
            invoice_numbers[:5]
        )

        return (
            f"I found {len(result)} conflicting "
            f"check{'s' if len(result) != 1 else ''} "
            f"across invoice"
            f"{'s' if len(invoice_numbers) != 1 else ''} "
            f"{preview}."
        )

    return None


def build_grounded_answer_prompt(
    question,
    tool_name,
    tool_result,
):
    result_json = json.dumps(
        tool_result,
        indent=2,
        ensure_ascii=False,
        default=str,
    )

    return f"""
You are Zaki, the chatbot inside DocuAgent.

Answer using ONLY the tool result below.

Do not invent values.
Do not use outside knowledge.
Keep the answer concise and user-friendly.

User question:
{question}

Tool:
{tool_name}

Result:
{result_json}

Return only the final answer.
"""


def generate_grounded_answer(
    question,
    tool_execution,
):
    if not tool_execution.get(
        "success"
    ):
        return (
            "I couldn't complete that "
            "document request."
        )

    tool_name = tool_execution[
        "tool_name"
    ]

    tool_result = tool_execution[
        "result"
    ]

    fast_answer = (
        format_deterministic_answer(
            question,
            tool_name,
            tool_result,
        )
    )

    if fast_answer is not None:
        return fast_answer

    prompt = (
        build_grounded_answer_prompt(
            question=question,
            tool_name=tool_name,
            tool_result=tool_result,
        )
    )

    response = ask_groq(
        prompt
    )

    if not response:
        return (
            "I found the data, but I couldn't "
            "prepare the response."
        )

    return response.strip()


def ask_zaki(question):
    selection = select_zaki_tool(
        question
    )

    if selection.get(
        "error"
    ):
        return {
            "question":
                question,
            "tool_selection":
                selection,
            "tool_execution":
                None,
            "answer": (
                "I couldn't determine which "
                "document operation should "
                "handle that question."
            ),
            "error":
                selection["error"],
        }

    execution = execute_zaki_tool(
        selection["tool_name"],
        selection.get(
            "arguments",
            {},
        ),
    )

    answer = generate_grounded_answer(
        question,
        execution,
    )

    return {
        "question": question,
        "tool_selection": selection,
        "tool_execution": execution,
        "answer": answer,
        "error": execution.get(
            "error"
        ),
    }
