from src.extraction import build_partial_scan_prompt

invoice_prompt = build_partial_scan_prompt(
    "TAX INVOICE Invoice No: INV-123 Total: 1140 EGP",
    "invoice",
    ["invoice_number", "total", "invalid_field"],
)

invalid_prompt = build_partial_scan_prompt(
    "Random text",
    "invoice",
    ["invalid_field"],
)

unknown_prompt = build_partial_scan_prompt(
    "Random text",
    "unknown",
    ["total"],
)

assert invoice_prompt is not None
assert '"invoice_number"' in invoice_prompt
assert '"total"' in invoice_prompt
assert "invalid_field" not in invoice_prompt

assert invalid_prompt is None
assert unknown_prompt is None

print("Partial scan prompt tests passed.")