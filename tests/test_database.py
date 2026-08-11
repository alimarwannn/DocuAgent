from src.database import (
    create_tables,
    list_documents,
)


create_tables()

documents = list_documents()

print("Saved documents:")
print(documents)

assert isinstance(documents, list)

for document in documents:
    assert "id" in document
    assert "filename" in document
    assert "document_type" in document
    assert "scan_mode" in document
    assert "created_at" in document

print("Database query test passed.")
