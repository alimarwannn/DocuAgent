from src.extraction import run_quick_scan

invoice_text = """
TAX INVOICE
Invoice Number: INV-123
Date: 2026-08-05
Total: 1140 EGP
"""

result = run_quick_scan(invoice_text, "invoice")

assert result["document_type"] == "invoice"
assert result["scan_mode"] == "quick"
assert "invoice_number" in result["fields"]
assert "date" in result["fields"]
assert "total" in result["fields"]

print("Quick scan result test passed.")
print(result)