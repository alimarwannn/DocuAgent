from uuid import uuid4

from src.database import (
    create_tables,
    save_document,
    save_extracted_fields,
)
from src.zaki_graph import run_zaki


create_tables()

unique_id = uuid4().hex[:8]
invoice_number = f"GRAPH-{unique_id}"

document_id = save_document(
    filename=f"zaki_graph_test_{unique_id}.jpg",
    document_type="invoice",
    scan_mode="full",
    raw_ocr_text="Zaki graph test invoice",
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
    "Are there duplicate invoices?",
    "Are there contradictions between my documents?",
]


for question in questions:
    print()
    print("USER:", question)

    result = run_zaki(question)

    print("TOOL:", result.get("tool_name"))
    print("ARGUMENTS:", result.get("tool_arguments"))
    print("ANSWER:", result.get("answer"))
    print("ERROR:", result.get("error"))

    assert result["error"] is None
    assert result["tool_name"] is not None
    assert result["tool_result"] is not None
    assert isinstance(result["answer"], str)
    assert len(result["answer"]) > 0


print()
print("Zaki LangGraph chatbot tests passed.")