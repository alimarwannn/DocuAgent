from collections import defaultdict

from src.database import (
    get_database_connection,
    get_document_fields,
    get_document_issues,
    list_documents,
)


def _to_float(value):
    if value in (None, ""):
        return None

    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def get_documents_with_fields():
    documents = list_documents()

    results = []

    for document in documents:
        document_data = dict(document)
        document_data["fields"] = get_document_fields(document["id"])
        results.append(document_data)

    return results


def total_spend(start_date=None, end_date=None):
    documents = get_documents_with_fields()

    total = 0.0
    matched_documents = []

    for document in documents:
        fields = document["fields"]

        document_date = fields.get("date")
        amount = _to_float(fields.get("total"))

        if amount is None:
            continue

        if start_date is not None:
            if document_date is None or document_date < start_date:
                continue

        if end_date is not None:
            if document_date is None or document_date > end_date:
                continue

        total += amount
        matched_documents.append(document)

    return {
        "total": total,
        "document_count": len(matched_documents),
        "documents": matched_documents,
    }


def total_tax(start_date=None, end_date=None):
    documents = get_documents_with_fields()

    total = 0.0
    matched_documents = []

    for document in documents:
        fields = document["fields"]

        document_date = fields.get("date")
        tax = _to_float(fields.get("tax"))

        if tax is None:
            continue

        if start_date is not None:
            if document_date is None or document_date < start_date:
                continue

        if end_date is not None:
            if document_date is None or document_date > end_date:
                continue

        total += tax
        matched_documents.append(document)

    return {
        "total_tax": total,
        "document_count": len(matched_documents),
        "documents": matched_documents,
    }


def average_document_value(start_date=None, end_date=None):
    spend_result = total_spend(start_date, end_date)

    count = spend_result["document_count"]

    if count == 0:
        average = 0.0
    else:
        average = spend_result["total"] / count

    return {
        "average": average,
        "document_count": count,
        "total": spend_result["total"],
    }


def highest_value_documents(limit=5):
    documents = get_documents_with_fields()

    valued_documents = []

    for document in documents:
        amount = _to_float(document["fields"].get("total"))

        if amount is None:
            continue

        document_data = dict(document)
        document_data["total"] = amount

        valued_documents.append(document_data)

    valued_documents.sort(
        key=lambda document: document["total"],
        reverse=True,
    )

    return valued_documents[:limit]


def supplier_summary():
    documents = get_documents_with_fields()

    summaries = defaultdict(
        lambda: {
            "document_count": 0,
            "total_value": 0.0,
        }
    )

    for document in documents:
        fields = document["fields"]

        supplier = (
            fields.get("supplier_name")
            or fields.get("merchant_name")
        )

        if not supplier:
            continue

        amount = _to_float(fields.get("total"))

        summaries[supplier]["document_count"] += 1

        if amount is not None:
            summaries[supplier]["total_value"] += amount

    results = []

    for supplier, data in summaries.items():
        results.append(
            {
                "supplier": supplier,
                "document_count": data["document_count"],
                "total_value": data["total_value"],
            }
        )

    results.sort(
        key=lambda item: item["document_count"],
        reverse=True,
    )

    return results


def invalid_documents():
    documents = list_documents()

    results = []

    for document in documents:
        issues = get_document_issues(document["id"])

        if not issues:
            continue

        document_data = dict(document)
        document_data["issues"] = issues

        results.append(document_data)

    return results


def duplicate_invoices():
    connection = get_database_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT
            field_value AS invoice_number,
            COUNT(*) AS occurrence_count
        FROM extracted_fields
        WHERE field_name = 'invoice_number'
          AND field_value IS NOT NULL
          AND TRIM(field_value) != ''
        GROUP BY field_value
        HAVING COUNT(*) > 1
        ORDER BY occurrence_count DESC
        """
    )

    duplicates = cursor.fetchall()

    results = []

    for duplicate in duplicates:
        invoice_number = duplicate["invoice_number"]

        cursor.execute(
            """
            SELECT DISTINCT d.*
            FROM documents d
            JOIN extracted_fields e
                ON d.id = e.document_id
            WHERE e.field_name = 'invoice_number'
              AND e.field_value = ?
            ORDER BY d.id
            """,
            (invoice_number,),
        )

        documents = [
            dict(row)
            for row in cursor.fetchall()
        ]

        results.append(
            {
                "invoice_number": invoice_number,
                "occurrence_count": duplicate["occurrence_count"],
                "documents": documents,
            }
        )

    connection.close()

    return results


def detect_contradictions():
    documents = get_documents_with_fields()

    invoice_groups = defaultdict(list)

    for document in documents:
        fields = document["fields"]

        invoice_number = fields.get("invoice_number")

        if not invoice_number:
            continue

        invoice_groups[invoice_number].append(document)

    contradictions = []

    for invoice_number, grouped_documents in invoice_groups.items():
        if len(grouped_documents) < 2:
            continue

        totals = set()
        suppliers = set()
        dates = set()

        for document in grouped_documents:
            fields = document["fields"]

            total = fields.get("total")
            supplier = fields.get("supplier_name")
            date = fields.get("date")

            if total not in (None, ""):
                totals.add(str(total))

            if supplier not in (None, ""):
                suppliers.add(str(supplier))

            if date not in (None, ""):
                dates.add(str(date))

        if len(totals) > 1:
            contradictions.append(
                {
                    "invoice_number": invoice_number,
                    "type": "conflicting_total",
                    "values": sorted(totals),
                    "document_ids": [
                        document["id"]
                        for document in grouped_documents
                    ],
                }
            )

        if len(suppliers) > 1:
            contradictions.append(
                {
                    "invoice_number": invoice_number,
                    "type": "conflicting_supplier",
                    "values": sorted(suppliers),
                    "document_ids": [
                        document["id"]
                        for document in grouped_documents
                    ],
                }
            )

        if len(dates) > 1:
            contradictions.append(
                {
                    "invoice_number": invoice_number,
                    "type": "conflicting_date",
                    "values": sorted(dates),
                    "document_ids": [
                        document["id"]
                        for document in grouped_documents
                    ],
                }
            )

    return contradictions