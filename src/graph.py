from langgraph.graph import (
    StateGraph,
    START,
    END,
)

from src.state import (
    DocumentState,
)

from src.graph_nodes import (
    load_node,
    ocr_node,
    document_type_node,
    scan_mode_router,
    error_router,
    full_scan_node,
    partial_scan_node,
    quick_scan_node,
    normalization_node,
    validation_node,
    review_router,
    human_review_node,
    save_node,
)


def build_document_graph():
    graph = StateGraph(
        DocumentState
    )

    graph.add_node(
        "load",
        load_node,
    )

    graph.add_node(
        "ocr",
        ocr_node,
    )

    graph.add_node(
        "document_type",
        document_type_node,
    )

    graph.add_node(
        "full_scan",
        full_scan_node,
    )

    graph.add_node(
        "partial_scan",
        partial_scan_node,
    )

    graph.add_node(
        "quick_scan",
        quick_scan_node,
    )

    graph.add_node(
        "normalization",
        normalization_node,
    )

    graph.add_node(
        "validation",
        validation_node,
    )

    graph.add_node(
        "human_review",
        human_review_node,
    )

    graph.add_node(
        "save",
        save_node,
    )

    graph.add_edge(
        START,
        "load",
    )

    graph.add_conditional_edges(
        "load",
        error_router,
        {
            "continue":
                "ocr",
            "error":
                END,
        },
    )

    graph.add_conditional_edges(
        "ocr",
        error_router,
        {
            "continue":
                "document_type",
            "error":
                END,
        },
    )

    graph.add_conditional_edges(
        "document_type",
        scan_mode_router,
        {
            "full":
                "full_scan",
            "partial":
                "partial_scan",
            "quick":
                "quick_scan",
            "error":
                END,
        },
    )

    graph.add_conditional_edges(
        "full_scan",
        error_router,
        {
            "continue":
                "normalization",
            "error":
                END,
        },
    )

    graph.add_conditional_edges(
        "partial_scan",
        error_router,
        {
            "continue":
                "normalization",
            "error":
                END,
        },
    )

    graph.add_edge(
        "quick_scan",
        END,
    )

    graph.add_conditional_edges(
        "normalization",
        error_router,
        {
            "continue":
                "validation",
            "error":
                END,
        },
    )

    graph.add_conditional_edges(
        "validation",
        review_router,
        {
            "review":
                "human_review",
            "save":
                "save",
            "error":
                END,
        },
    )

    graph.add_edge(
        "human_review",
        END,
    )

    graph.add_edge(
        "save",
        END,
    )

    return graph.compile()