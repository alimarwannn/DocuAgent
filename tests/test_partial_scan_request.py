from src.extraction import run_partial_scan_from_request

invoice_text = """
TAX INVOICE
Supplier: Vodafone Egypt
Invoice No: INV-123
Date: 2026-08-05
Subtotal: 1000
Tax: 140
Total: 1140 EGP
"""

result = run_partial_scan_from_request(
    invoice_text,
    "invoice",
    "Extract the invoice number, total, and currency.",
)


print("RESULT:")
print(result)
print("TOTAL VALUE:")
print(repr(result["fields"]["total"]))
print("TOTAL TYPE:")
print(type(result["fields"]["total"]))

assert result is not None
assert result["document_type"] == "invoice"
assert result["scan_mode"] == "partial"
assert result["fields"]["invoice_number"] == "INV-123"
assert result["fields"]["total"] == 1140
assert result["fields"]["currency"] == "EGP"
assert "supplier_name" not in result["fields"]

print("Natural-language partial scan result:")
print(result)

print("\nNatural-language partial scan test passed.")