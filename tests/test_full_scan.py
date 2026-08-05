from src.extraction import run_full_scan

invoice_text = """
TAX INVOICE
Supplier: Vodafone Egypt
Invoice No: INV-123
Date: 2026-08-05
Subtotal: 1000
Tax: 140
Total: 1140 EGP
"""

result = run_full_scan(invoice_text, "invoice")
unknown_result = run_full_scan(invoice_text, "unknown")

assert result is not None
assert isinstance(result, dict)
assert result["document_type"] == "invoice"
assert result["scan_mode"] == "full"
assert result["fields"]["invoice_number"] == "INV-123"
assert result["fields"]["total"] == 1140
assert result["fields"]["currency"] == "EGP"
assert unknown_result is None

print("Parsed full scan result:")
print(result)

print("\nFull scan API test passed.")