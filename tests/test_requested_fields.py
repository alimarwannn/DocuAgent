from src.extraction import parse_requested_fields

invoice_fields = parse_requested_fields(
    "Extract the invoice number, total, and currency.",
    "invoice",
)

receipt_fields = parse_requested_fields(
    "Give me the merchant name and payment method.",
    "receipt",
)

empty_fields = parse_requested_fields("", "invoice")
unknown_fields = parse_requested_fields("Extract total", "unknown")

assert invoice_fields == [
    "invoice_number",
    "total",
    "currency",
]

assert receipt_fields == [
    "merchant_name",
    "payment_method",
]

assert empty_fields == []
assert unknown_fields == []

print("Requested-field parsing tests passed.")
print(invoice_fields)
print(receipt_fields)