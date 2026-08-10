from uuid import uuid4

from src.database import (
    create_tables,
    filter_documents_by_amount,
    filter_documents_by_date,
    filter_documents_by_party,
    filter_documents_by_type,
    find_document_by_number,
    get_document,
    get_document_fields,
    get_document_issues,
    list_documents,
    save_document,
    save_extracted_fields,
    save_validation_issues,
)


create_tables()

unique_id = uuid4().hex[:8]

invoice_number = f"QUERY-{unique_id}"

document_id = save_document(
    filename=f"query_test_{unique_id}.jpg",
    document_type="invoice",
    scan_mode="full",
    raw_ocr_text=f"Invoice No: {invoice_number}",
)

save_extracted_fields(
    document_id,
    {
        "supplier_name": "Vodafone Egypt",
        "invoice_number": invoice_number,
        "date": "2026-08-05",
        "customer": None,
        "subtotal": 1000,
        "tax": 140,
        "total": 1200,
        "currency": "EGP",
    },
)

save_validation_issues(
    document_id,
    [
        {
            "issue_type": "total_mismatch",
            "message": "Subtotal plus tax is 1140, but total is 1200.",
            "severity": "error",
        }
    ],
)


documents = list_documents()
assert isinstance(documents, list)
assert any(document["id"] == document_id for document in documents)


document = get_document(document_id)
assert document["id"] == document_id


fields = get_document_fields(document_id)
assert fields["supplier_name"] == "Vodafone Egypt"
assert fields["invoice_number"] == invoice_number


issues = get_document_issues(document_id)
assert issues[0]["issue_type"] == "total_mismatch"


invoice_documents = filter_documents_by_type("invoice")
assert any(document["id"] == document_id for document in invoice_documents)


date_documents = filter_documents_by_date(
    "2026-08-01",
    "2026-08-10",
)
assert any(document["id"] == document_id for document in date_documents)


party_documents = filter_documents_by_party("Vodafone")
assert any(document["id"] == document_id for document in party_documents)


number_documents = find_document_by_number(invoice_number)
assert any(document["id"] == document_id for document in number_documents)


amount_documents = filter_documents_by_amount(
    minimum_amount=1000,
)
assert any(document["id"] == document_id for document in amount_documents)


range_documents = filter_documents_by_amount(
    minimum_amount=1100,
    maximum_amount=1300,
)
assert any(document["id"] == document_id for document in range_documents)


print("Database query and filter tests passed.")