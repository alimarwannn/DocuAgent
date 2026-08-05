from src.validation import validate_total_consistency

valid_fields = {
    "subtotal": 1000,
    "tax": 140,
    "total": 1140,
}

invalid_fields = {
    "subtotal": 1000,
    "tax": 140,
    "total": 1200,
}

missing_fields = {
    "subtotal": 1000,
    "tax": None,
    "total": 1140,
}

valid_issues = validate_total_consistency(valid_fields)
invalid_issues = validate_total_consistency(invalid_fields)
missing_issues = validate_total_consistency(missing_fields)

assert valid_issues == []
assert len(invalid_issues) == 1
assert invalid_issues[0]["issue_type"] == "total_mismatch"
assert invalid_issues[0]["severity"] == "error"
assert missing_issues == []

print("Total consistency validation tests passed.")
print(invalid_issues)