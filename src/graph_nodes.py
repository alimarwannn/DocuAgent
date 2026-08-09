from src.state import DocumentState


def load_node(state: DocumentState):
    image_path = state.get("image_path")

    if not image_path:
        return {
            "error": "Missing image path."
        }

    return {
        "image_path": image_path
    }