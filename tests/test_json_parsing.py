from src.extraction import parse_groq_json

valid_response = (
    "```json\n"
    "{\n"
    '    "supplier_name": "Vodafone Egypt",\n'
    '    "invoice_number": "INV-123",\n'
    '    "total": 1140,\n'
    '    "currency": "EGP"\n'
    "}\n"
    "```"
)

invalid_response = "This is not valid JSON"

parsed_result = parse_groq_json(valid_response)
invalid_result = parse_groq_json(invalid_response)
empty_result = parse_groq_json(None)

assert isinstance(parsed_result, dict)
assert parsed_result["invoice_number"] == "INV-123"
assert parsed_result["total"] == 1140
assert invalid_result is None
assert empty_result is None

print("JSON parsing tests passed.")
print(parsed_result)