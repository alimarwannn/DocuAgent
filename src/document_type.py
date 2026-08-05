def detect_document_type(ocr_text):
    text = ocr_text.lower()

    if "invoice" in text:
        return "invoice"

    if "receipt" in text:
        return "receipt"

    return "unknown"