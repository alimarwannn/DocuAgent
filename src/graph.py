from langgraph.graph import StateGraph, START, END

from src.state import DocumentState
from src.graph_nodes import (
    load_node,
    ocr_node,
    document_type_node,
    scan_mode_router,
    full_scan_node,
    partial_scan_node,
    quick_scan_node,
    validation_node,
    save_node,
)


def build_document_graph():
    graph = StateGraph(DocumentState)

    graph.add_node("load", load_node)
    graph.add_node("ocr", ocr_node)
    graph.add_node("document_type", document_type_node)
    graph.add_node("full_scan", full_scan_node)
    graph.add_node("partial_scan", partial_scan_node)
    graph.add_node("quick_scan", quick_scan_node)
    graph.add_node("validation", validation_node)
    graph.add_node("save", save_node)

    graph.add_edge(START, "load")
    graph.add_edge("load", "ocr")
    graph.add_edge("ocr", "document_type")

    graph.add_conditional_edges(
        "document_type",
        scan_mode_router,
        {
            "full": "full_scan",
            "partial": "partial_scan",
            "quick": "quick_scan",
            "error": END,
        },
    )

    graph.add_edge("full_scan", "validation")
    graph.add_edge("partial_scan", "validation")
    graph.add_edge("quick_scan", END)

    graph.add_edge("validation", "save")
    graph.add_edge("save", END)

    return graph.compile()