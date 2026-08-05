def detect_document_type(ocr_text):
    if not ocr_text:
        return "unknown"

    text = ocr_text.lower()

    if "invoice" in text:
        return "invoice"

    if "receipt" in text:
        return "receipt"

    return "unknown"

