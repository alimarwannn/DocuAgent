from src.extraction import validate_extracted_fields

invoice_data = {
    "supplier_name": "Vodafone Egypt",
    "invoice_number": "INV-123",
    "total": 1140,
    "currency": "EGP",
    "unexpected_field": "remove me",
}

validated_invoice = validate_extracted_fields(invoice_data, "invoice")
invalid_result = validate_extracted_fields("not a dictionary", "invoice")
unknown_result = validate_extracted_fields(invoice_data, "unknown")

assert validated_invoice["supplier_name"] == "Vodafone Egypt"
assert validated_invoice["invoice_number"] == "INV-123"
assert validated_invoice["total"] == 1140
assert validated_invoice["customer"] is None
assert "unexpected_field" not in validated_invoice

assert invalid_result is None
assert unknown_result is None

print("Field validation tests passed.")
print(validated_invoice)