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
    "MYR": "MYR",
    "RM": "MYR",
}


def normalize_currency(
    value,
    raw_ocr_text=None,
):
    # Important:
    # Do not infer a missing currency from raw OCR.
    #
    # Currency grounding is handled during extraction.
    # If extraction could not verify a currency,
    # None must remain None so validation can send
    # the document for human review.

    if value is None:
        return None

    if not isinstance(
        value,
        str,
    ):
        return value

    cleaned_value = (
        value
        .strip()
        .upper()
    )

    if not cleaned_value:
        return None

    # Prefer exact aliases first.
    if (
        cleaned_value
        in CURRENCY_ALIASES
    ):
        return CURRENCY_ALIASES[
            cleaned_value
        ]

    # Support values such as:
    # "RM 193.00"
    # "USD $"
    # "EGP currency"
    #
    # This only normalizes the provided value.
    # It does NOT search raw OCR text.
    for (
        alias,
        normalized,
    ) in (
        CURRENCY_ALIASES.items()
    ):
        if re.search(
            rf"\b{re.escape(alias)}\b",
            cleaned_value,
        ):
            return normalized

    return cleaned_value


def normalize_date(value):
    if not isinstance(
        value,
        str,
    ):
        return value

    cleaned_value = (
        value.strip()
    )

    if not cleaned_value:
        return None

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
            parsed_date = (
                datetime.strptime(
                    cleaned_value,
                    date_format,
                )
            )

            return parsed_date.strftime(
                "%Y-%m-%d"
            )

        except ValueError:
            continue

    return cleaned_value


def normalize_fields(
    fields,
    raw_ocr_text=None,
):
    if not isinstance(
        fields,
        dict,
    ):
        return fields

    normalized_fields = (
        fields.copy()
    )

    if "currency" in normalized_fields:
        normalized_fields[
            "currency"
        ] = normalize_currency(
            normalized_fields.get(
                "currency"
            ),
            raw_ocr_text,
        )

    if "date" in normalized_fields:
        normalized_fields[
            "date"
        ] = normalize_date(
            normalized_fields.get(
                "date"
            )
        )

    return normalized_fields