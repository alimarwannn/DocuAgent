from typing import TypedDict

from langgraph.graph import END, START, StateGraph

from src.zaki_chat import generate_grounded_answer
from src.zaki_executor import execute_zaki_tool
from src.zaki_router import select_zaki_tool


class ZakiState(TypedDict, total=False):
    question: str
    tool_name: str | None
    tool_arguments: dict
    tool_reason: str
    tool_result: dict | list | None
    answer: str
    error: str | None


def select_tool_node(state: ZakiState):
    question = state.get("question", "")

    selection = select_zaki_tool(question)

    return {
        "tool_name": selection.get("tool_name"),
        "tool_arguments": selection.get("arguments", {}),
        "tool_reason": selection.get("reason", ""),
        "error": selection.get("error"),
    }


def route_after_selection(state: ZakiState):
    if state.get("error") or not state.get("tool_name"):
        return "selection_error"

    return "execute_tool"


def execute_tool_node(state: ZakiState):
    execution = execute_zaki_tool(
        state["tool_name"],
        state.get("tool_arguments", {}),
    )

    if not execution.get("success"):
        return {
            "tool_result": None,
            "error": execution.get(
                "error",
                "tool_execution_failed",
            ),
        }

    return {
        "tool_result": execution,
        "error": None,
    }


def route_after_execution(state: ZakiState):
    if state.get("error"):
        return "execution_error"

    return "generate_answer"


def generate_answer_node(state: ZakiState):
    execution = state["tool_result"]

    answer = generate_grounded_answer(
        state["question"],
        execution,
    )

    return {
        "answer": answer,
        "error": None,
    }


def selection_error_node(state: ZakiState):
    return {
        "answer": (
            "I couldn't determine which document tool "
            "should handle that question."
        )
    }


def execution_error_node(state: ZakiState):
    return {
        "answer": (
            "I understood the question, but I couldn't "
            "complete the database operation."
        )
    }


def build_zaki_graph():
    graph = StateGraph(ZakiState)

    graph.add_node(
        "select_tool",
        select_tool_node,
    )

    graph.add_node(
        "execute_tool",
        execute_tool_node,
    )

    graph.add_node(
        "generate_answer",
        generate_answer_node,
    )

    graph.add_node(
        "selection_error",
        selection_error_node,
    )

    graph.add_node(
        "execution_error",
        execution_error_node,
    )

    graph.add_edge(
        START,
        "select_tool",
    )

    graph.add_conditional_edges(
        "select_tool",
        route_after_selection,
        {
            "execute_tool": "execute_tool",
            "selection_error": "selection_error",
        },
    )

    graph.add_conditional_edges(
        "execute_tool",
        route_after_execution,
        {
            "generate_answer": "generate_answer",
            "execution_error": "execution_error",
        },
    )

    graph.add_edge(
        "generate_answer",
        END,
    )

    graph.add_edge(
        "selection_error",
        END,
    )

    graph.add_edge(
        "execution_error",
        END,
    )

    return graph.compile()


zaki_graph = build_zaki_graph()


def run_zaki(question):
    result = zaki_graph.invoke(
        {
            "question": question,
            "tool_name": None,
            "tool_arguments": {},
            "tool_reason": "",
            "tool_result": None,
            "answer": "",
            "error": None,
        }
    )

    return result