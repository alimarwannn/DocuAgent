from src.extraction import (
    run_full_scan,
    run_partial_scan,
    run_partial_scan_from_request,
    run_quick_scan,
)

assert run_full_scan("Random text", "unknown") is None

assert run_partial_scan(
    "Random text",
    "unknown",
    ["total"],
) is None

assert run_partial_scan(
    "Random text",
    "invoice",
    ["invalid_field"],
) is None

assert run_partial_scan_from_request(
    "Random text",
    "invoice",
    "Extract an unsupported field.",
) is None

quick_result = run_quick_scan("", "invoice")

assert quick_result["document_type"] == "invoice"
assert quick_result["scan_mode"] == "quick"
assert quick_result["fields"] == []

print("Invalid scan input tests passed.")