import re
from datetime import datetime


CURRENCY_ALIASES = {
    "SR": "SAR",
    "SAR": "SAR",
    "EGP": "EGP",
    "USD": "USD",
    "EUR": "EUR",
    "GBP": "GBP",
    "QAR": "QAR",
}


def normalize_currency(value, raw_ocr_text=None):
    if isinstance(value, str):
        cleaned_value = value.strip().upper()

        for alias, normalized in CURRENCY_ALIASES.items():
            if re.search(rf"\b{re.escape(alias)}\b", cleaned_value):
                return normalized

    if isinstance(raw_ocr_text, str):
        text = raw_ocr_text.upper()

        for alias, normalized in CURRENCY_ALIASES.items():
            if re.search(rf"\b{re.escape(alias)}\b", text):
                return normalized

    if isinstance(value, str):
        return value.strip().upper()

    return value


def normalize_date(value):
    if not isinstance(value, str):
        return value

    cleaned_value = value.strip()

    formats = [
        "%Y-%m-%d",
        "%Y-%m-%d %H:%M:%S",
        "%d/%m/%Y",
        "%d/%m/%Y %I:%M:%S %p",
        "%d/%m/%Y %I:%M.%S %p",
        "%d/%m/%Y %H:%M:%S",
        "%d-%m-%Y",
    ]

    for date_format in formats:
        try:
            parsed_date = datetime.strptime(
                cleaned_value,
                date_format,
            )

            return parsed_date.strftime("%Y-%m-%d")
        except ValueError:
            continue

    return cleaned_value


def normalize_fields(fields, raw_ocr_text=None):
    if not isinstance(fields, dict):
        return fields

    normalized_fields = fields.copy()

    normalized_fields["currency"] = normalize_currency(
        normalized_fields.get("currency"),
        raw_ocr_text,
    )

    normalized_fields["date"] = normalize_date(
        normalized_fields.get("date")
    )

    return normalized_fields