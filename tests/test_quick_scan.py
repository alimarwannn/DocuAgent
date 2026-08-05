from src.extraction import suggest_available_fields

invoice_text = """
TAX INVOICE
Invoice Number: INV-123
Date: 2026-08-05
Subtotal: 1000
Tax: 140
Total: 1140 EGP
"""

receipt_text = """
PAYMENT RECEIPT
Merchant Name: Vodafone Store
Receipt Number: REC-456
Payment Method: Card
Total: 228 EGP
"""

invoice_fields = suggest_available_fields(invoice_text, "invoice")
receipt_fields = suggest_available_fields(receipt_text, "receipt")
empty_fields = suggest_available_fields("", "invoice")
unknown_fields = suggest_available_fields("Total: 100", "unknown")

assert "invoice_number" in invoice_fields
assert "date" in invoice_fields
assert "subtotal" in invoice_fields
assert "tax" in invoice_fields
assert "total" in invoice_fields

assert "merchant_name" in receipt_fields
assert "receipt_number" in receipt_fields
assert "payment_method" in receipt_fields
assert "total" in receipt_fields

assert empty_fields == []
assert unknown_fields == []

print("Quick scan field suggestion tests passed.")
print(invoice_fields)
print(receipt_fields)