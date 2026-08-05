from src.extraction import run_partial_scan

invoice_text = """
TAX INVOICE
Supplier: Vodafone Egypt
Invoice No: INV-123
Date: 2026-08-05
Subtotal: 1000
Tax: 140
Total: 1140 EGP
"""

result = run_partial_scan(
    invoice_text,
    "invoice",
    ["invoice_number", "total", "currency"],
)

assert result is not None
assert result["document_type"] == "invoice"
assert result["scan_mode"] == "partial"
assert result["fields"]["invoice_number"] == "INV-123"
assert result["fields"]["total"] == 1140
assert result["fields"]["currency"] == "EGP"
assert "supplier_name" not in result["fields"]

print("Partial scan result:")
print(result)

print("\nPartial scan API test passed.")