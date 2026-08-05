from src.schemas import INVOICE_TEMPLATE, RECEIPT_TEMPLATE


def create_empty_result(document_type, scan_mode):
    if document_type == "invoice":
        fields = INVOICE_TEMPLATE.copy()
    elif document_type == "receipt":
        fields = RECEIPT_TEMPLATE.copy()
    else:
        fields = {}

    return {
        "document_type": document_type,
        "scan_mode": scan_mode,
        "fields": fields,

    }
import json


def build_full_scan_prompt(ocr_text, document_type):
    if document_type == "invoice":
        fields = list(INVOICE_TEMPLATE.keys())
    elif document_type == "receipt":
        fields = list(RECEIPT_TEMPLATE.keys())
    else:
        return None

    return f"""
Extract structured data from this {document_type}.

Return only valid JSON.
Use exactly these fields:
{json.dumps(fields)}

Use null when a value is missing.
Do not guess values.

OCR text:
{ocr_text}
""".strip()