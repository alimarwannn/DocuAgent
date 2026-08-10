import json

from src.groq_client import ask_groq
from src.zaki_executor import execute_zaki_tool
from src.zaki_router import select_zaki_tool


def build_grounded_answer_prompt(question, tool_name, tool_result):
    result_json = json.dumps(
        tool_result,
        indent=2,
        ensure_ascii=False,
        default=str,
    )

    return f"""
You are Zaki, the chatbot inside DocuAgent.

Answer the user's question using ONLY the tool result provided below.

Rules:
- Do not invent values.
- Do not use outside knowledge.
- Do not perform new calculations if the tool result already contains the answer.
- If the tool result is empty, clearly say that no matching documents were found.
- If the tool failed, explain that the database query could not be completed.
- Mention useful document IDs or filenames when available.
- Keep the answer concise and clear.

User question:
{question}

Tool used:
{tool_name}

Tool result:
{result_json}

Return only the final answer for the user.
"""


def generate_grounded_answer(question, tool_execution):
    if not tool_execution.get("success"):
        return (
            "I couldn't complete that database query. "
            f"Error: {tool_execution.get('error', 'unknown_error')}."
        )

    prompt = build_grounded_answer_prompt(
        question=question,
        tool_name=tool_execution["tool_name"],
        tool_result=tool_execution["result"],
    )

    response = ask_groq(prompt)

    if not response:
        return "I found the data, but I couldn't generate a response."

    return response.strip()


def ask_zaki(question):
    selection = select_zaki_tool(question)

    if selection.get("error"):
        return {
            "question": question,
            "tool_selection": selection,
            "tool_execution": None,
            "answer": (
                "I couldn't determine which document tool "
                "should handle that question."
            ),
            "error": selection["error"],
        }

    execution = execute_zaki_tool(
        selection["tool_name"],
        selection.get("arguments", {}),
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
        "error": execution.get("error"),
    }