from src.normalization import (
    normalize_currency,
    normalize_date,
    normalize_fields,
)


# Explicit values can still be normalized.
assert (
    normalize_currency("SR")
    == "SAR"
)

assert (
    normalize_currency("sar")
    == "SAR"
)

assert (
    normalize_currency(" EGP ")
    == "EGP"
)

assert (
    normalize_currency("RM")
    == "MYR"
)

assert (
    normalize_currency("myr")
    == "MYR"
)


# Text supplied as the actual currency value
# can still contain an alias.
assert (
    normalize_currency(
        "UNKNOWN (SR IS MENTIONED)"
    )
    == "SAR"
)


# Date normalization.
assert (
    normalize_date(
        "15/01/2019 11:05:16 AM"
    )
    == "2019-01-15"
)

assert (
    normalize_date(
        "15/01/2019 11:05.16 AM"
    )
    == "2019-01-15"
)

assert (
    normalize_date(
        "15/01/2019"
    )
    == "2019-01-15"
)

assert (
    normalize_date(
        "2019-01-15"
    )
    == "2019-01-15"
)


# Important safety test:
# normalization must NOT invent a currency
# from raw OCR when extraction returned None.
fields = {
    "date":
        "15/01/2019 11:05.16 AM",

    "currency":
        None,

    "total":
        193.0,
}


ocr_text = """
TOTAL:
193.00 SR
"""


normalized = normalize_fields(
    fields,
    ocr_text,
)


assert (
    normalized["date"]
    == "2019-01-15"
)

assert (
    normalized["currency"]
    is None
)

assert (
    normalized["total"]
    == 193.0
)


print(
    "Normalization tests passed."
)