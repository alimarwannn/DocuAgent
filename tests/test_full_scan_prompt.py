from src.extraction import build_full_scan_prompt

invoice_prompt = build_full_scan_prompt(
    "TAX INVOICE Invoice No: 123 Total: 500 EGP",
    "invoice",
)

receipt_prompt = build_full_scan_prompt(
    "PAYMENT RECEIPT Total: 250 EGP",
    "receipt",
)

unknown_prompt = build_full_scan_prompt(
    "Random document text",
    "unknown",
)

assert invoice_prompt is not None
assert '"invoice_number"' in invoice_prompt
assert "TAX INVOICE" in invoice_prompt

assert receipt_prompt is not None
assert '"merchant_name"' in receipt_prompt
assert "PAYMENT RECEIPT" in receipt_prompt

assert unknown_prompt is None

print("Full scan prompt tests passed.")