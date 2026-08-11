from src.extraction import (
    ground_extracted_fields,
)


ocr_text = """
OJC MARKETING SDN BHD
TAX INVOICE

Invoice No
PEGIV-1030765

Date
15/01/2019 11:05.16 AM

Total Exclude GST:
193.00

Total GST @6%
0.00

Total Inclusive GST:
193.00

TOTAL:
193.00

VISA CARD
193.00
"""


fields = {
    "merchant_name":
        "OJC MARKETING SDN BHD",

    "receipt_number":
        None,

    "date":
        "2019-01-15",

    "subtotal":
        7.95,

    "tax":
        7.5,

    "total":
        1020,

    "payment_method":
        "VISA CARD",

    "currency":
        "SAR",
}


grounded = (
    ground_extracted_fields(
        fields,
        ocr_text,
        "receipt",
    )
)


assert (
    grounded[
        "receipt_number"
    ]
    == "PEGIV-1030765"
)


assert (
    grounded[
        "subtotal"
    ]
    == 193.0
)


assert (
    grounded[
        "tax"
    ]
    == 0.0
)


assert (
    grounded[
        "total"
    ]
    == 193.0
)


assert (
    grounded[
        "currency"
    ]
    is None
)


assert (
    grounded[
        "date"
    ]
    == "2019-01-15"
)


print(
    "Extraction grounding tests passed."
)