from src.document_type import detect_document_type

invoice_text = "TAX INVOICE Invoice No: 12345"
receipt_text = "PAYMENT RECEIPT Total: 250"
unknown_text = "Random document text"

assert detect_document_type(invoice_text) == "invoice"
assert detect_document_type(receipt_text) == "receipt"
assert detect_document_type(unknown_text) == "unknown"

print("Document type tests passed.")

assert detect_document_type(None) == "unknown"
assert detect_document_type("") == "unknown"