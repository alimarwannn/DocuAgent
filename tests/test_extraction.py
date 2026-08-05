from src.extraction import create_empty_result

invoice_result = create_empty_result("invoice", "full")
receipt_result = create_empty_result("receipt", "partial")
unknown_result = create_empty_result("unknown", "quick")

assert invoice_result["document_type"] == "invoice"
assert invoice_result["scan_mode"] == "full"
assert invoice_result["fields"]["invoice_number"] is None

assert receipt_result["document_type"] == "receipt"
assert receipt_result["scan_mode"] == "partial"
assert receipt_result["fields"]["merchant_name"] is None

assert unknown_result["fields"] == {}

print("Extraction template tests passed.")