from src.schemas import (
    INVOICE_FIELDS,
    RECEIPT_FIELDS,
    INVOICE_TEMPLATE,
    RECEIPT_TEMPLATE,
)
from src.groq_client import ask_groq


def run_full_scan(ocr_text, document_type):
    prompt = build_full_scan_prompt(ocr_text, document_type)

    if prompt is None:
        return None
    response_text = ask_groq(prompt)
    
    parsed_fields = parse_groq_json(response_text)
    

    validated_fields = validate_extracted_fields(
        parsed_fields,
        document_type,
    )

    if validated_fields is None:
        return None

    return {
        "document_type": document_type,
        "scan_mode": "full",
        "fields": validated_fields,
    }
    



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



def validate_extracted_fields(extracted_fields, document_type):
    if not isinstance(extracted_fields, dict):
        return None

    if document_type == "invoice":
        allowed_fields = INVOICE_FIELDS
    elif document_type == "receipt":
        allowed_fields = RECEIPT_FIELDS
    else:
        return None

    return {
        field: extracted_fields.get(field)
        for field in allowed_fields
    }

def build_partial_scan_prompt(ocr_text, document_type, requested_fields):
    if document_type == "invoice":
        allowed_fields = INVOICE_FIELDS
    elif document_type == "receipt":
        allowed_fields = RECEIPT_FIELDS
    else:
        return None

    valid_fields = [
        field for field in requested_fields
        if field in allowed_fields
    ]

    if not valid_fields:
        return None

    return f"""
Extract only the requested fields from this {document_type}.

Return only valid JSON.
Use exactly these fields:
{json.dumps(valid_fields)}

Use null when a requested value is missing.
Do not add extra fields.
Do not guess values.

OCR text:
{ocr_text}
""".strip()

def run_partial_scan(ocr_text, document_type, requested_fields):
    prompt = build_partial_scan_prompt(
        ocr_text,
        document_type,
        requested_fields,
    )

    if prompt is None:
        return None

    response_text = ask_groq(prompt)
    parsed_fields = parse_groq_json(response_text)

    if not isinstance(parsed_fields, dict):
        return None

    valid_fields = {
        field: parsed_fields.get(field)
        for field in requested_fields
        if field in parsed_fields
    }

    return {
        "document_type": document_type,
        "scan_mode": "partial",
        "fields": valid_fields,
    }


def parse_requested_fields(user_request, document_type):
    if not user_request:
        return []

    request_text = user_request.lower()

    if document_type == "invoice":
        allowed_fields = INVOICE_FIELDS
    elif document_type == "receipt":
        allowed_fields = RECEIPT_FIELDS
    else:
        return []

    matched_fields = []

    for field in allowed_fields:
        readable_name = field.replace("_", " ")

        if field in request_text or readable_name in request_text:
            matched_fields.append(field)

    return matched_fields