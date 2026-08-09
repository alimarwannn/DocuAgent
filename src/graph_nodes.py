from src.state import DocumentState
from src.ocr import extract_text


def load_node(state: DocumentState):
    image_path = state.get("image_path")

    if not image_path:
        return {
            "error": "Missing image path."
        }

    return {
        "image_path": image_path
    }

def ocr_node(state: DocumentState):
    image_path = state.get("image_path")

    if not image_path:
        return {
            "error": "Cannot run OCR without image path."
        }

    ocr_result = extract_text(image_path)

    if ocr_result is None:
        return {
            "error": "OCR failed."
        }

    return {
        "raw_ocr_text": ocr_result["raw_text"]
    }