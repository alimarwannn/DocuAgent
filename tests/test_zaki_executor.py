from uuid import uuid4

from src.database import (
    create_tables,
    save_document,
    save_extracted_fields,
)
from src.zaki_executor import execute_zaki_tool


create_tables()

unique_id = uuid4().hex[:8]
invoice_number = f"EXECUTOR-{unique_id}"

document_id = save_document(
    filename=f"executor_test_{unique_id}.jpg",
    document_type="invoice",
    scan_mode="full",
    raw_ocr_text="Executor test invoice",
)

save_extracted_fields(
    document_id,
    {
        "supplier_name": "Vodafone Egypt",
        "invoice_number": invoice_number,
        "date": "2026-08-10",
        "subtotal": 1000,
        "tax": 140,
        "total": 1140,
        "currency": "EGP",
    },
)


result = execute_zaki_tool(
    "find_document_by_number",
    {
        "document_number": invoice_number,
    },
)

assert result["success"] is True
assert result["tool_name"] == "find_document_by_number"
assert any(
    document["id"] == document_id
    for document in result["result"]
)


result = execute_zaki_tool(
    "filter_documents_by_amount",
    {
        "minimum_amount": 1000,
        "maximum_amount": None,
    },
)

assert result["success"] is True
assert any(
    document["id"] == document_id
    for document in result["result"]
)


result = execute_zaki_tool(
    "total_spend",
    {
        "start_date": "2026-08-10",
        "end_date": "2026-08-10",
    },
)

assert result["success"] is True
assert result["result"]["total"] >= 1140


result = execute_zaki_tool(
    "highest_value_documents",
    {
        "limit": 3,
    },
)

assert result["success"] is True
assert len(result["result"]) <= 3


result = execute_zaki_tool(
    "duplicate_invoices",
    {},
)

assert result["success"] is True


result = execute_zaki_tool(
    "not_a_real_tool",
    {},
)

assert result["success"] is False
assert result["error"] == "unknown_tool"


print("Zaki tool executor tests passed.")