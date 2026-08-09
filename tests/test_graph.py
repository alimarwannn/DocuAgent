from src.graph import build_document_graph

graph = build_document_graph()

assert graph is not None

print("LangGraph compilation test passed.")