import json

from src.schemas import (
    INVOICE_FIELDS,
    RECEIPT_FIELDS,
    INVOICE_TEMPLATE,
    RECEIPT_TEMPLATE,
)

from src.groq_client import ask_groq


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


def build_full_scan_prompt(ocr_text, document_type):
    if document_type == "invoice":
        fields = list(INVOICE_TEMPLATE.keys())
    elif document_type == "receipt":
        fields = list(RECEIPT_TEMPLATE.keys())
    else:
        return None

    return f"""
Extract structured data from this {document_type}.

Return only one valid JSON object.
Do not use markdown.
Do not use code fences.
Do not include explanations.

Use exactly these fields:
{json.dumps(fields)}

Rules:
- Use null when a value is missing.
- Do not guess values.
- Numeric amounts must be JSON numbers, not strings.
- Return only the JSON object.

OCR text:
{ocr_text}
""".strip()


def parse_groq_json(response_text):
    if not isinstance(response_text, str):
        return None

    cleaned_text = response_text.strip()

    if cleaned_text.startswith("```"):
        cleaned_text = cleaned_text.replace("```json", "")
        cleaned_text = cleaned_text.replace("```JSON", "")
        cleaned_text = cleaned_text.replace("```", "")
        cleaned_text = cleaned_text.strip()

    start_index = cleaned_text.find("{")
    end_index = cleaned_text.rfind("}")

    if start_index == -1 or end_index == -1:
        return None

    json_text = cleaned_text[
        start_index:end_index + 1
    ]

    try:
        parsed = json.loads(json_text)
    except json.JSONDecodeError:
        return None

    if not isinstance(parsed, dict):
        return None

    return parsed


def validate_extracted_fields(
    extracted_fields,
    document_type,
):
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


def run_full_scan(
    ocr_text,
    document_type,
):
    prompt = build_full_scan_prompt(
        ocr_text,
        document_type,
    )

    if prompt is None:
        return None

    for _ in range(3):
        try:
            response_text = ask_groq(prompt)
        except Exception:
            continue

        parsed_fields = parse_groq_json(
            response_text
        )

        if parsed_fields is None:
            continue

        validated_fields = validate_extracted_fields(
            parsed_fields,
            document_type,
        )

        if validated_fields is None:
            continue

        return {
            "document_type": document_type,
            "scan_mode": "full",
            "fields": validated_fields,
        }

    return None


def build_partial_scan_prompt(
    ocr_text,
    document_type,
    requested_fields,
):
    if document_type == "invoice":
        allowed_fields = INVOICE_FIELDS
    elif document_type == "receipt":
        allowed_fields = RECEIPT_FIELDS
    else:
        return None

    valid_fields = [
        field
        for field in requested_fields
        if field in allowed_fields
    ]

    if not valid_fields:
        return None

    return f"""
Extract only the requested fields from this {document_type}.

Return only one valid JSON object.
Do not use markdown.
Do not use code fences.
Do not include explanations.

Use exactly these fields:
{json.dumps(valid_fields)}

Rules:
- Use null when a requested value is missing.
- Do not add extra fields.
- Do not guess values.
- Numeric amounts must be JSON numbers, not strings.
- Return only the JSON object.

OCR text:
{ocr_text}
""".strip()


def run_partial_scan(
    ocr_text,
    document_type,
    requested_fields,
):
    prompt = build_partial_scan_prompt(
        ocr_text,
        document_type,
        requested_fields,
    )

    if prompt is None:
        return None

    for _ in range(3):
        try:
            response_text = ask_groq(prompt)
        except Exception:
            continue

        parsed_fields = parse_groq_json(
            response_text
        )

        if parsed_fields is None:
            continue

        partial_fields = {
            field: parsed_fields.get(field)
            for field in requested_fields
        }

        return {
            "document_type": document_type,
            "scan_mode": "partial",
            "fields": partial_fields,
        }

    return None


def parse_requested_fields(
    user_request,
    document_type,
):
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
        readable_name = field.replace(
            "_",
            " ",
        )

        if (
            field in request_text
            or readable_name in request_text
        ):
            matched_fields.append(field)

    return matched_fields


def run_partial_scan_from_request(
    ocr_text,
    document_type,
    user_request,
):
    requested_fields = parse_requested_fields(
        user_request,
        document_type,
    )

    if not requested_fields:
        return None

    return run_partial_scan(
        ocr_text,
        document_type,
        requested_fields,
    )


def suggest_available_fields(
    ocr_text,
    document_type,
):
    if not ocr_text:
        return []

    text = ocr_text.lower()

    if document_type == "invoice":
        allowed_fields = INVOICE_FIELDS
    elif document_type == "receipt":
        allowed_fields = RECEIPT_FIELDS
    else:
        return []

    suggested_fields = []

    for field in allowed_fields:
        readable_name = field.replace(
            "_",
            " ",
        )

        if field == "tax":
            tax_lines = [
                line.strip()
                for line in text.splitlines()
            ]

            if any(
                line.startswith("tax:")
                or (
                    line.startswith("tax ")
                    and not line.startswith(
                        "tax invoice"
                    )
                )
                or line.startswith("vat")
                for line in tax_lines
            ):
                suggested_fields.append(field)

        elif (
            field in text
            or readable_name in text
        ):
            suggested_fields.append(field)

    return suggested_fields


def run_quick_scan(
    ocr_text,
    document_type,
):
    suggested_fields = suggest_available_fields(
        ocr_text,
        document_type,
    )

    return {
        "document_type": document_type,
        "scan_mode": "quick",
        "fields": suggested_fields,
    }