from src.extraction import run_partial_scan

receipt_text = """
PAYMENT RECEIPT
Merchant: Vodafone Store
Receipt No: REC-456
Date: 2026-08-05
Total: 228 EGP
Payment Method: Card
"""

result = run_partial_scan(
    receipt_text,
    "receipt",
    ["merchant_name", "total", "payment_method"],
)

assert result is not None
assert result["document_type"] == "receipt"
assert result["scan_mode"] == "partial"
assert result["fields"]["merchant_name"] == "Vodafone Store"
assert result["fields"]["total"] == 228
assert "receipt_number" not in result["fields"]

print("Receipt partial scan test passed.")
print(result)
