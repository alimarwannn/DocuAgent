import re


INVOICE_SIGNALS = {
    "invoice number": 5,
    "invoice no": 5,
    "invoice #": 5,
    "invoice date": 4,
    "bill to": 4,
    "billing address": 3,
    "due date": 4,
    "amount due": 3,
    "purchase order": 4,
    "po number": 4,
    "po no": 4,
    "payment terms": 3,
    "customer number": 3,
    "customer id": 3,
}


RECEIPT_SIGNALS = {
    "receipt number": 5,
    "receipt no": 5,
    "receipt #": 5,
    "cashier": 4,
    "cash": 2,
    "change": 4,
    "tender": 4,
    "thank you": 3,
    "payment method": 3,
    "payment type": 3,
    "qty": 2,
    "quantity": 2,
    "unit price": 2,
    "item": 1,
    "gst": 2,
    "vat": 1,
    "subtotal": 1,
    "sub total": 1,
    "grand total": 2,
}


def _contains_phrase(
    text,
    phrase,
):
    return phrase in text


def _score_signals(
    text,
    signals,
):
    score = 0

    for (
        phrase,
        weight,
    ) in signals.items():
        if _contains_phrase(
            text,
            phrase,
        ):
            score += weight

    return score


def detect_document_type(
    ocr_text,
):
    if not ocr_text:
        return "unknown"

    text = (
        str(
            ocr_text
        )
        .lower()
    )

    # Normalize OCR spacing.
    text = re.sub(
        r"\s+",
        " ",
        text,
    )

    invoice_score = (
        _score_signals(
            text,
            INVOICE_SIGNALS,
        )
    )

    receipt_score = (
        _score_signals(
            text,
            RECEIPT_SIGNALS,
        )
    )

    if re.search(
        r"\breceipt\b",
        text,
    ):
        receipt_score += 5

    if re.search(
        r"\binvoice\b",
        text,
    ):
        invoice_score += 2

    # "Tax invoice" is common on retail receipts,
    # so it must not automatically force invoice.
    if "tax invoice" in text:
        invoice_score += 1

        retail_markers = [
            "cash",
            "cashier",
            "change",
            "qty",
            "quantity",
            "thank you",
            "gst",
            "subtotal",
            "grand total",
            "tender",
        ]

        retail_count = sum(
            1
            for marker
            in retail_markers
            if marker in text
        )

        if retail_count >= 2:
            receipt_score += 5

    # A receipt normally contains several retail
    # transaction signals rather than only one.
    retail_marker_count = sum(
        1
        for marker
        in [
            "cash",
            "cashier",
            "change",
            "qty",
            "quantity",
            "unit price",
            "thank you",
            "gst",
            "tender",
            "subtotal",
        ]
        if marker in text
    )

    if retail_marker_count >= 3:
        receipt_score += 3

    if (
        receipt_score == 0
        and invoice_score == 0
    ):
        return "unknown"

    if receipt_score > invoice_score:
        return "receipt"

    if invoice_score > receipt_score:
        return "invoice"

    # When scores tie, require stronger evidence
    # rather than silently choosing the wrong type.
    return "unknown"