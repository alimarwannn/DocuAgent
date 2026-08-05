from src.validation import validate_currency

valid_uppercase = {
    "currency": "EGP",
}

valid_lowercase = {
    "currency": "egp",
}

invalid_currency = {
    "currency": "ABC",
}

invalid_type = {
    "currency": 123,
}

missing_currency = {
    "currency": None,
}

assert validate_currency(valid_uppercase) == []
assert validate_currency(valid_lowercase) == []

invalid_currency_issues = validate_currency(invalid_currency)
invalid_type_issues = validate_currency(invalid_type)
missing_issues = validate_currency(missing_currency)

assert len(invalid_currency_issues) == 1
assert invalid_currency_issues[0]["issue_type"] == "invalid_currency"

assert len(invalid_type_issues) == 1
assert invalid_type_issues[0]["issue_type"] == "invalid_currency"

assert missing_issues == []

print("Currency validation tests passed.")
print(invalid_currency_issues)
print(invalid_type_issues)