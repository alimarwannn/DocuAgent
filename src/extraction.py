from src.schemas import INVOICE_TEMPLATE, RECEIPT_TEMPLATE
from src.groq_client import ask_groq


def run_full_scan(ocr_text, document_type):
    prompt = build_full_scan_prompt(ocr_text, document_type)

    if prompt is None:
        return None

    return ask_groq(prompt)


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

def parse_groq_json(response_text):
    if not response_text:
        return None

    cleaned_text = response_text.strip()

    if cleaned_text.startswith("```json"):
        cleaned_text = cleaned_text[7:]

    if cleaned_text.startswith("```"):
        cleaned_text = cleaned_text[3:]

    if cleaned_text.endswith("```"):
        cleaned_text = cleaned_text[:-3]

    cleaned_text = cleaned_text.strip()

    try:
        return json.loads(cleaned_text)
    except json.JSONDecodeError:
        return None
    