from uuid import uuid4

from src.database import (
    create_tables,
    save_document,
    save_extracted_fields,
)
from src.zaki_chat import ask_zaki


create_tables()

unique_id = uuid4().hex[:8]
invoice_number = f"ZAKI-{unique_id}"

document_id = save_document(
    filename=f"zaki_chat_test_{unique_id}.jpg",
    document_type="invoice",
    scan_mode="full",
    raw_ocr_text="Zaki chatbot test invoice",
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


questions = [
    f"Find invoice {invoice_number}.",
    "What was the total tax?",
    "Which suppliers appear most often?",
    "Show me the 3 highest value documents.",
    "Are there duplicate invoices?",
    "Are there contradictions between my documents?",
]


for question in questions:
    print()
    print("USER:", question)

    result = ask_zaki(question)

    print("TOOL:", result["tool_selection"]["tool_name"])
    print("ANSWER:", result["answer"])

    assert result["tool_execution"] is not None
    assert result["tool_execution"]["success"] is True
    assert isinstance(result["answer"], str)
    assert len(result["answer"]) > 0


print()
print("Zaki full chatbot tests passed.")