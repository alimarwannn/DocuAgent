import json
import re
from datetime import datetime
from decimal import Decimal, InvalidOperation

from src.schemas import (
    INVOICE_FIELDS,
    RECEIPT_FIELDS,
    INVOICE_TEMPLATE,
    RECEIPT_TEMPLATE,
)

from src.groq_client import ask_groq


FIELD_ALIASES = {
    "supplier_name": [
        "supplier",
        "supplier name",
        "vendor",
        "vendor name",
        "company",
    ],
    "merchant_name": [
        "merchant",
        "merchant name",
        "shop",
        "store",
        "company",
    ],
    "invoice_number": [
        "invoice number",
        "invoice no",
        "invoice no.",
        "invoice id",
        "invoice reference",
    ],
    "receipt_number": [
        "receipt number",
        "receipt no",
        "receipt no.",
        "receipt id",
        "transaction number",
        "transaction no",
        "reference number",
        "bill number",
        "invoice number",
        "invoice no",
    ],
    "date": [
        "date",
        "invoice date",
        "receipt date",
        "transaction date",
    ],
    "customer": [
        "customer",
        "customer name",
        "client",
        "client name",
        "bill to",
    ],
    "subtotal": [
        "subtotal",
        "sub total",
        "total exclude",
        "total before tax",
    ],
    "tax": [
        "tax",
        "vat",
        "gst",
        "sales tax",
    ],
    "total": [
        "total",
        "grand total",
        "amount due",
        "final amount",
        "total inclusive",
    ],
    "payment_method": [
        "payment method",
        "payment",
        "paid by",
        "cash",
        "card",
        "visa",
        "mastercard",
    ],
    "currency": [
        "currency",
        "egp",
        "usd",
        "eur",
        "gbp",
        "qar",
        "sar",
        "myr",
        "rm",
    ],
}


def create_empty_result(
    document_type,
    scan_mode,
):
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


def build_full_scan_prompt(
    ocr_text,
    document_type,
):
    if document_type == "invoice":
        fields = list(
            INVOICE_TEMPLATE.keys()
        )

    elif document_type == "receipt":
        fields = list(
            RECEIPT_TEMPLATE.keys()
        )

    else:
        return None

    receipt_rule = ""

    if document_type == "receipt":
        receipt_rule = """
- Some retail receipts are titled "Tax Invoice".
- If such a receipt has an invoice number, it may be used
  as receipt_number because it identifies the transaction.
"""

    return f"""
Extract structured data from this {document_type}.

Return exactly one valid JSON object.
Do not use markdown.
Do not use code fences.
Do not include explanations.

Use exactly these fields:
{json.dumps(fields)}

STRICT RULES:

- Use ONLY information supported directly by the OCR text.
- If a value is uncertain or missing, return null.
- Never invent, calculate, estimate, or guess values.

Financial values:
- Copy amounts exactly as printed.
- Preserve decimal points.
- Do not calculate missing values.
- Numeric amounts must be JSON numbers.

Currency:
- Only return currency when its code or symbol is visible.
- RM means MYR.
- Never infer currency from company name, address or country.

Dates:
- Return YYYY-MM-DD when a clear date is present.

{receipt_rule}

Return only the JSON object.

OCR TEXT:
----------------
{ocr_text}
----------------
""".strip()


def parse_groq_json(
    response_text,
):
    if not isinstance(
        response_text,
        str,
    ):
        return None

    cleaned_text = (
        response_text.strip()
    )

    if cleaned_text.startswith("```"):
        cleaned_text = (
            cleaned_text
            .replace(
                "```json",
                "",
            )
            .replace(
                "```JSON",
                "",
            )
            .replace(
                "```",
                "",
            )
            .strip()
        )

    start_index = (
        cleaned_text.find("{")
    )

    end_index = (
        cleaned_text.rfind("}")
    )

    if (
        start_index == -1
        or end_index == -1
    ):
        return None

    json_text = cleaned_text[
        start_index:
        end_index + 1
    ]

    try:
        parsed = json.loads(
            json_text
        )

    except json.JSONDecodeError:
        return None

    if not isinstance(
        parsed,
        dict,
    ):
        return None

    return parsed


def validate_extracted_fields(
    extracted_fields,
    document_type,
):
    if not isinstance(
        extracted_fields,
        dict,
    ):
        return None

    if document_type == "invoice":
        allowed_fields = (
            INVOICE_FIELDS
        )

    elif document_type == "receipt":
        allowed_fields = (
            RECEIPT_FIELDS
        )

    else:
        return None

    return {
        field:
            extracted_fields.get(
                field
            )
        for field in allowed_fields
    }


# ---------------------------------------------------------
# NUMERIC HELPERS
# ---------------------------------------------------------

def _to_decimal(value):
    if isinstance(
        value,
        bool,
    ):
        return None

    if isinstance(
        value,
        (int, float, Decimal),
    ):
        try:
            return Decimal(
                str(value)
            )

        except InvalidOperation:
            return None

    if not isinstance(
        value,
        str,
    ):
        return None

    cleaned = (
        value
        .strip()
        .replace(",", "")
    )

    try:
        return Decimal(
            cleaned
        )

    except InvalidOperation:
        return None


def _numbers_from_text(text):
    if not text:
        return []

    matches = re.findall(
        r"""
        (?<![A-Za-z0-9])
        -?
        (?:
            \d{1,3}
            (?:,\d{3})+
            (?:\.\d+)?
            |
            \d+
            (?:\.\d+)?
        )
        (?![A-Za-z0-9])
        """,
        text,
        flags=re.VERBOSE,
    )

    numbers = []

    for match in matches:
        value = _to_decimal(
            match
        )

        if value is not None:
            numbers.append(
                value
            )

    return numbers


def _standalone_amount(line):
    if not line:
        return None

    cleaned = (
        line
        .strip()
        .replace(",", "")
    )

    match = re.match(
        r"""
        ^
        (?:
            RM\s*
            |
            MYR\s*
            |
            EGP\s*
            |
            USD\s*
            |
            EUR\s*
            |
            GBP\s*
            |
            QAR\s*
            |
            SAR\s*
            |
            [$€£]\s*
        )?
        (-?\d+(?:\.\d+)?)
        (?:
            \s*
            (?:
                RM|
                MYR|
                EGP|
                USD|
                EUR|
                GBP|
                QAR|
                SAR
            )
        )?
        [.:]?
        $
        """,
        cleaned,
        flags=(
            re.IGNORECASE
            | re.VERBOSE
        ),
    )

    if not match:
        return None

    return _to_decimal(
        match.group(1)
    )


def _next_amount(
    lines,
    index,
    max_lookahead=2,
):
    for offset in range(
        1,
        max_lookahead + 1,
    ):
        target_index = (
            index + offset
        )

        if target_index >= len(
            lines
        ):
            break

        amount = (
            _standalone_amount(
                lines[
                    target_index
                ]
            )
        )

        if amount is not None:
            return amount

    return None


def _same_line_amount(line):
    numbers = (
        _numbers_from_text(
            line
        )
    )

    if not numbers:
        return None

    return numbers[-1]


# ---------------------------------------------------------
# FINANCIAL RECOVERY
# ---------------------------------------------------------

def _recover_subtotal(
    ocr_text,
):
    lines = [
        line.strip()
        for line
        in ocr_text.splitlines()
        if line.strip()
    ]

    markers = [
        "subtotal",
        "sub total",
        "sub-total",
        "total exclude",
        "total before tax",
    ]

    for index, line in enumerate(
        lines
    ):
        lowered = line.lower()

        if not any(
            marker in lowered
            for marker in markers
        ):
            continue

        following = (
            _next_amount(
                lines,
                index,
            )
        )

        if following is not None:
            return following

        same_line = (
            _same_line_amount(
                line
            )
        )

        if same_line is not None:
            return same_line

    return None


def _recover_tax(
    ocr_text,
):
    lines = [
        line.strip()
        for line
        in ocr_text.splitlines()
        if line.strip()
    ]

    markers = [
        "tax:",
        "tax amount",
        "total tax",
        "vat",
        "vat amount",
        "gst amount",
        "total gst",
        "sales tax",
    ]

    for index, line in enumerate(
        lines
    ):
        lowered = line.lower()

        if not any(
            marker in lowered
            for marker in markers
        ):
            continue

        if any(
            excluded in lowered
            for excluded in [
                "exclude gst",
                "inclusive gst",
                "subtotal",
            ]
        ):
            continue

        # Prefer the next OCR line because
        # label lines often contain tax percentages.
        following = (
            _next_amount(
                lines,
                index,
            )
        )

        if following is not None:
            return following

        if (
            "%"
            not in line
            and "@"
            not in line
        ):
            same_line = (
                _same_line_amount(
                    line
                )
            )

            if same_line is not None:
                return same_line

    return None


def _recover_total(
    ocr_text,
):
    lines = [
        line.strip()
        for line
        in ocr_text.splitlines()
        if line.strip()
    ]

    # Search backwards because the final payable
    # total is normally near the end of a receipt.
    for index in range(
        len(lines) - 1,
        -1,
        -1,
    ):
        line = lines[
            index
        ]

        lowered = (
            line
            .lower()
            .strip()
        )

        excluded = [
            "exclude",
            "subtotal",
            "sub total",
            "gst",
            "tax",
            "round",
        ]

        if any(
            word in lowered
            for word in excluded
        ):
            continue

        valid_total_label = (
            lowered in {
                "total",
                "total:",
                "grand total",
                "grand total:",
                "amount due",
                "amount due:",
                "net total",
                "net total:",
            }
            or lowered.startswith(
                "total inclusive"
            )
            or lowered.startswith(
                "total:"
            )
            or lowered.startswith(
                "grand total:"
            )
            or lowered.startswith(
                "amount due:"
            )
            or lowered.startswith(
                "net total:"
            )
        )

        if not valid_total_label:
            continue

        following = (
            _next_amount(
                lines,
                index,
            )
        )

        if following is not None:
            return following

        same_line = (
            _same_line_amount(
                line
            )
        )

        if same_line is not None:
            return same_line

    return None


# ---------------------------------------------------------
# DATE RECOVERY
# ---------------------------------------------------------

def _parse_date_candidate(
    value,
):
    if not isinstance(
        value,
        str,
    ):
        return None

    value = (
        value.strip()
    )

    formats = [
        "%Y-%m-%d",
        "%Y/%m/%d",
        "%d/%m/%Y",
        "%d-%m-%Y",
        "%d.%m.%Y",
        "%d/%m/%y",
        "%d-%m-%y",
    ]

    for date_format in formats:
        try:
            parsed = (
                datetime.strptime(
                    value,
                    date_format,
                )
            )

            return (
                parsed.strftime(
                    "%Y-%m-%d"
                )
            )

        except ValueError:
            continue

    return None


def _extract_date_from_text(
    text,
):
    if not text:
        return None

    patterns = [
        r"\b\d{4}[-/]\d{1,2}[-/]\d{1,2}\b",
        r"\b\d{1,2}[/.-]\d{1,2}[/.-]\d{4}\b",
        r"\b\d{1,2}[/.-]\d{1,2}[/.-]\d{2}\b",
    ]

    for pattern in patterns:
        matches = re.findall(
            pattern,
            text,
        )

        for match in matches:
            normalized = (
                _parse_date_candidate(
                    match
                )
            )

            if normalized:
                return normalized

    return None


def _recover_date(
    ocr_text,
):
    if not ocr_text:
        return None

    lines = [
        line.strip()
        for line
        in ocr_text.splitlines()
        if line.strip()
    ]

    date_labels = [
        "date",
        "invoice date",
        "receipt date",
        "transaction date",
    ]

    # First prefer a date close to an explicit Date label.
    for index, line in enumerate(
        lines
    ):
        lowered = (
            line.lower()
        )

        if not any(
            label in lowered
            for label in date_labels
        ):
            continue

        same_line_date = (
            _extract_date_from_text(
                line
            )
        )

        if same_line_date:
            return same_line_date

        for offset in [
            1,
            2,
        ]:
            next_index = (
                index + offset
            )

            if next_index >= len(
                lines
            ):
                break

            next_line_date = (
                _extract_date_from_text(
                    lines[
                        next_index
                    ]
                )
            )

            if next_line_date:
                return next_line_date

    # Fallback: use the first valid printed date.
    return _extract_date_from_text(
        ocr_text
    )


# ---------------------------------------------------------
# DOCUMENT NUMBER RECOVERY
# ---------------------------------------------------------

def _recover_document_number(
    ocr_text,
    document_type,
):
    lines = [
        line.strip()
        for line
        in ocr_text.splitlines()
        if line.strip()
    ]

    if document_type == "receipt":
        labels = [
            "receipt no",
            "receipt number",
            "transaction no",
            "transaction number",
            "invoice no",
            "invoice number",
        ]

    else:
        labels = [
            "invoice no",
            "invoice number",
        ]

    for index, line in enumerate(
        lines
    ):
        lowered = (
            line.lower()
        )

        if not any(
            label in lowered
            for label in labels
        ):
            continue

        for label in labels:
            position = (
                lowered.find(
                    label
                )
            )

            if position == -1:
                continue

            remainder = (
                line[
                    position
                    + len(label):
                ]
                .strip(
                    " :#-"
                )
            )

            if (
                remainder
                and re.search(
                    r"\d",
                    remainder,
                )
            ):
                return remainder

        for offset in [
            1,
            2,
        ]:
            next_index = (
                index + offset
            )

            if next_index >= len(
                lines
            ):
                break

            candidate = (
                lines[
                    next_index
                ]
                .strip()
            )

            if (
                re.search(
                    r"\d",
                    candidate,
                )
                and len(
                    candidate
                ) <= 40
            ):
                return candidate

    return None


# ---------------------------------------------------------
# CURRENCY GROUNDING
# ---------------------------------------------------------

def _currency_from_ocr(
    ocr_text,
):
    text = str(
        ocr_text
    )

    patterns = {
        "EGP":
            r"(?<![A-Za-z])EGP(?![A-Za-z])",

        "USD":
            r"(?<![A-Za-z])USD(?![A-Za-z])|US\$",

        "EUR":
            r"(?<![A-Za-z])EUR(?![A-Za-z])|€",

        "GBP":
            r"(?<![A-Za-z])GBP(?![A-Za-z])|£",

        "QAR":
            r"(?<![A-Za-z])QAR(?![A-Za-z])",

        "SAR":
            r"(?<![A-Za-z])SAR(?![A-Za-z])",

        "MYR":
            (
                r"(?<![A-Za-z])MYR(?![A-Za-z])"
                r"|(?<![A-Za-z])RM(?=\s*\d)"
            ),
    }

    detected = []

    for (
        currency,
        pattern,
    ) in patterns.items():
        if re.search(
            pattern,
            text,
            flags=re.IGNORECASE,
        ):
            detected.append(
                currency
            )

    if len(detected) == 1:
        return detected[0]

    return None


# ---------------------------------------------------------
# GROUNDING
# ---------------------------------------------------------

def ground_extracted_fields(
    fields,
    ocr_text,
    document_type,
):
    grounded = (
        fields.copy()
    )

    recovered_amounts = {
        "subtotal":
            _recover_subtotal(
                ocr_text
            ),

        "tax":
            _recover_tax(
                ocr_text
            ),

        "total":
            _recover_total(
                ocr_text
            ),
    }

    for (
        field_name,
        recovered_value,
    ) in recovered_amounts.items():

        if field_name not in grounded:
            continue

        if recovered_value is not None:
            grounded[
                field_name
            ] = float(
                recovered_value
            )

        else:
            grounded[
                field_name
            ] = None

    if "date" in grounded:
        grounded[
            "date"
        ] = _recover_date(
            ocr_text
        )

    if "currency" in grounded:
        grounded[
            "currency"
        ] = _currency_from_ocr(
            ocr_text
        )

    number_field = (
        "invoice_number"
        if document_type
        == "invoice"
        else "receipt_number"
    )

    if number_field in grounded:
        recovered_number = (
            _recover_document_number(
                ocr_text,
                document_type,
            )
        )

        if recovered_number:
            grounded[
                number_field
            ] = recovered_number

    return grounded


# ---------------------------------------------------------
# FULL SCAN
# ---------------------------------------------------------

def run_full_scan(
    ocr_text,
    document_type,
):
    prompt = (
        build_full_scan_prompt(
            ocr_text,
            document_type,
        )
    )

    if prompt is None:
        return None

    for _ in range(3):
        try:
            response_text = (
                ask_groq(
                    prompt
                )
            )

        except Exception:
            continue

        parsed_fields = (
            parse_groq_json(
                response_text
            )
        )

        if parsed_fields is None:
            continue

        validated_fields = (
            validate_extracted_fields(
                parsed_fields,
                document_type,
            )
        )

        if validated_fields is None:
            continue

        grounded_fields = (
            ground_extracted_fields(
                validated_fields,
                ocr_text,
                document_type,
            )
        )

        return {
            "document_type":
                document_type,

            "scan_mode":
                "full",

            "fields":
                grounded_fields,
        }

    return None


# ---------------------------------------------------------
# PARTIAL SCAN
# ---------------------------------------------------------

def build_partial_scan_prompt(
    ocr_text,
    document_type,
    requested_fields,
):
    if document_type == "invoice":
        allowed_fields = (
            INVOICE_FIELDS
        )

    elif document_type == "receipt":
        allowed_fields = (
            RECEIPT_FIELDS
        )

    else:
        return None

    valid_fields = [
        field
        for field
        in requested_fields
        if field
        in allowed_fields
    ]

    if not valid_fields:
        return None

    return f"""
Extract only the requested fields from this {document_type}.

Return exactly one valid JSON object.
Do not use markdown.
Do not use code fences.
Do not include explanations.

Use exactly these fields:
{json.dumps(valid_fields)}

STRICT RULES:

- Use only values directly supported by OCR text.
- Use null when uncertain or missing.
- Never guess, infer, calculate, or estimate.
- Copy financial amounts exactly as printed.
- Numeric amounts must be JSON numbers.
- Only return currency when explicitly visible.
- RM means MYR.
- Never infer currency from company or country.
- Do not add fields that were not requested.

Return only the JSON object.

OCR TEXT:
----------------
{ocr_text}
----------------
""".strip()


def run_partial_scan(
    ocr_text,
    document_type,
    requested_fields,
):
    if document_type == "invoice":
        allowed_fields = (
            INVOICE_FIELDS
        )

    elif document_type == "receipt":
        allowed_fields = (
            RECEIPT_FIELDS
        )

    else:
        return None

    valid_fields = [
        field
        for field
        in requested_fields
        if field
        in allowed_fields
    ]

    prompt = (
        build_partial_scan_prompt(
            ocr_text,
            document_type,
            valid_fields,
        )
    )

    if prompt is None:
        return None

    for _ in range(3):
        try:
            response_text = (
                ask_groq(
                    prompt
                )
            )

        except Exception:
            continue

        parsed_fields = (
            parse_groq_json(
                response_text
            )
        )

        if parsed_fields is None:
            continue

        partial_fields = {
            field:
                parsed_fields.get(
                    field
                )
            for field
            in valid_fields
        }

        grounded_fields = (
            ground_extracted_fields(
                partial_fields,
                ocr_text,
                document_type,
            )
        )

        return {
            "document_type":
                document_type,

            "scan_mode":
                "partial",

            "fields":
                grounded_fields,
        }

    return None


def parse_requested_fields(
    user_request,
    document_type,
):
    if not user_request:
        return []

    request_text = (
        user_request.lower()
    )

    if document_type == "invoice":
        allowed_fields = (
            INVOICE_FIELDS
        )

    elif document_type == "receipt":
        allowed_fields = (
            RECEIPT_FIELDS
        )

    else:
        return []

    matched_fields = []

    for field in allowed_fields:
        aliases = [
            field,
            field.replace(
                "_",
                " ",
            ),
        ]

        aliases.extend(
            FIELD_ALIASES.get(
                field,
                [],
            )
        )

        if any(
            alias.lower()
            in request_text
            for alias
            in aliases
        ):
            matched_fields.append(
                field
            )

    return matched_fields


def run_partial_scan_from_request(
    ocr_text,
    document_type,
    user_request,
):
    requested_fields = (
        parse_requested_fields(
            user_request,
            document_type,
        )
    )

    if not requested_fields:
        return None

    return run_partial_scan(
        ocr_text,
        document_type,
        requested_fields,
    )


# ---------------------------------------------------------
# QUICK SCAN
# ---------------------------------------------------------

def suggest_available_fields(
    ocr_text,
    document_type,
):
    if not ocr_text:
        return []

    text = (
        ocr_text.lower()
    )

    if document_type == "invoice":
        allowed_fields = (
            INVOICE_FIELDS
        )

    elif document_type == "receipt":
        allowed_fields = (
            RECEIPT_FIELDS
        )

    else:
        return []

    suggested_fields = []

    for field in allowed_fields:
        aliases = [
            field,
            field.replace(
                "_",
                " ",
            ),
        ]

        aliases.extend(
            FIELD_ALIASES.get(
                field,
                [],
            )
        )

        if any(
            alias.lower()
            in text
            for alias
            in aliases
        ):
            suggested_fields.append(
                field
            )

    deterministic_checks = {
        "date":
            _recover_date(
                ocr_text
            ),

        "subtotal":
            _recover_subtotal(
                ocr_text
            ),

        "tax":
            _recover_tax(
                ocr_text
            ),

        "total":
            _recover_total(
                ocr_text
            ),

        "currency":
            _currency_from_ocr(
                ocr_text
            ),
    }

    for (
        field_name,
        detected_value,
    ) in deterministic_checks.items():

        if (
            field_name
            in allowed_fields
            and detected_value
            is not None
            and field_name
            not in suggested_fields
        ):
            suggested_fields.append(
                field_name
            )

    return suggested_fields


def run_quick_scan(
    ocr_text,
    document_type,
):
    suggested_fields = (
        suggest_available_fields(
            ocr_text,
            document_type,
        )
    )

    return {
        "document_type":
            document_type,

        "scan_mode":
            "quick",

        "fields":
            suggested_fields,

        "suggested_fields":
            suggested_fields,
    }