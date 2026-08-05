from src.validation import validate_date

valid_date = {
    "date": "2026-08-05",
}

wrong_format = {
    "date": "05/08/2026",
}

impossible_date = {
    "date": "2026-13-40",
}

invalid_type = {
    "date": 20260805,
}

missing_date = {
    "date": None,
}

assert validate_date(valid_date) == []

wrong_format_issues = validate_date(wrong_format)
impossible_date_issues = validate_date(impossible_date)
invalid_type_issues = validate_date(invalid_type)

assert len(wrong_format_issues) == 1
assert wrong_format_issues[0]["issue_type"] == "invalid_date"

assert len(impossible_date_issues) == 1
assert impossible_date_issues[0]["issue_type"] == "invalid_date"

assert len(invalid_type_issues) == 1
assert invalid_type_issues[0]["issue_type"] == "invalid_date"

assert validate_date(missing_date) == []

print("Date validation tests passed.")
print(wrong_format_issues)
print(impossible_date_issues)