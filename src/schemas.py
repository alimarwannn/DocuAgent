INVOICE_FIELDS = [
    "supplier_name",
    "invoice_number",
    "date",
    "customer",
    "subtotal",
    "tax",
    "total",
    "currency",
]

RECEIPT_FIELDS = [
    "merchant_name",
    "receipt_number",
    "date",
    "subtotal",
    "tax",
    "total",
    "payment_method",
    "currency",
]

INVOICE_REQUIRED_FIELDS = [
    "supplier_name",
    "invoice_number",
    "date",
    "total",
    "currency",
]

RECEIPT_REQUIRED_FIELDS = [
    "merchant_name",
    "date",
    "total",
    "currency",
]

INVOICE_TEMPLATE = {
    field: None for field in INVOICE_FIELDS
}

RECEIPT_TEMPLATE = {
    field: None for field in RECEIPT_FIELDS
}