from src.validation import validate_positive_amounts

valid_fields = {
    "subtotal": 1000,
    "tax": 140,
    "total": 1140,
}

invalid_fields = {
    "subtotal": -100,
    "tax": "140",
    "total": 40,
}

valid_issues = validate_positive_amounts(valid_fields)
invalid_issues = validate_positive_amounts(invalid_fields)
empty_issues = validate_positive_amounts({})

assert valid_issues == []
assert len(invalid_issues) == 2
assert invalid_issues[0]["issue_type"] == "invalid_amount"
assert invalid_issues[1]["issue_type"] == "invalid_amount"
assert empty_issues == []

print("Positive amount validation tests passed.")
print(invalid_issues)