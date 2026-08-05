from src.extraction import run_full_scan

receipt_text = """
PAYMENT RECEIPT
Merchant: Vodafone Store
Receipt No: REC-456
Date: 2026-08-05
Subtotal: 200
Tax: 28
Total: 228 EGP
Payment Method: Card
"""

result = run_full_scan(receipt_text, "receipt")

assert result is not None
assert result["document_type"] == "receipt"
assert result["scan_mode"] == "full"
assert result["fields"]["merchant_name"] == "Vodafone Store"
assert result["fields"]["receipt_number"] == "REC-456"
assert result["fields"]["total"] == 228
assert result["fields"]["currency"] == "EGP"

print("Parsed receipt result:")
print(result)

print("\nReceipt full scan test passed.")